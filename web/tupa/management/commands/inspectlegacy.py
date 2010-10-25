import keyword
from optparse import make_option
import re
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection

class Command(NoArgsCommand):
    help = "Introspects the database tables in the given database and outputs a Django model module."

    option_list = NoArgsCommand.option_list + (
        make_option('--database', action='store', dest='database', help='Nominates a database to '
                'introspect.  Defaults to using the "default" database.'),
    )

    requires_model_validation = False

    db_module = 'django.db'
    def handle_noargs(self, **options):
        source=open( "legacy/models.py" , "r" )
        koodi=source.read()
        source.close()        
        try:
            koodi=self.handle_inspection(options,koodi)
            source=open( "legacy/models.py","w" )
            source.write(koodi)
        except NotImplementedError:
            raise CommandError("Database inspection isn't supported for the currently selected database backend.")

    def handle_inspection(self, options,koodi):
        table2model = lambda table_name: table_name.title().replace('_', '').replace(' ', '').replace('-', '')

        cursor = connection.cursor()

        for table_name in connection.introspection.get_table_list(cursor):

            #yield 'class %s(models.Model):' % table2model(table_name)
            luokka =table2model(table_name).replace("Tupa","")
            #print luokka
            runko = ""
            sisennys_haku =  re.search('.*?(?=#gen_legacy_class ' + luokka +'\n)',koodi)
            sisennys=""
            if sisennys_haku:
                sisennys=len(sisennys_haku.group(0)) * " "

            try:
                relations = connection.introspection.get_relations(cursor, table_name)
            except NotImplementedError:
                relations = {}
            try:
                indexes = connection.introspection.get_indexes(cursor, table_name)
            except NotImplementedError:
                indexes = {}
            for i, row in enumerate(connection.introspection.get_table_description(cursor, table_name)):
                column_name = row[0]
                att_name = column_name.lower()
                comment_notes = [] # Holds Field notes, to be displayed in a Python comment.
                extra_params = {}  # Holds Field parameters such as 'db_column'.

                # If the column name can't be used verbatim as a Python
                # attribute, set the "db_column" for this Field.
                if ' ' in att_name or '-' in att_name or keyword.iskeyword(att_name) or column_name != att_name:
                    extra_params['db_column'] = column_name

                # Modify the field name to make it Python-compatible.
                if ' ' in att_name:
                    att_name = att_name.replace(' ', '_')
                    comment_notes.append('Field renamed to remove spaces.')
                if '-' in att_name:
                    att_name = att_name.replace('-', '_')
                    comment_notes.append('Field renamed to remove dashes.')
                if keyword.iskeyword(att_name):
                    att_name += '_field'
                    comment_notes.append('Field renamed because it was a Python reserved word.')
                if column_name != att_name:
                    comment_notes.append('Field name made lowercase.')

                if i in relations:
                    rel_to = relations[i][1] == table_name and "'self'" or table2model(relations[i][1])
                    field_type = 'ForeignKey(%s' % rel_to
                    if att_name.endswith('_id'):
                        att_name = att_name[:-3]
                    else:
                        extra_params['db_column'] = column_name
                else:
                    # Calling `get_field_type` to get the field type string and any
                    # additional paramters and notes.
                    field_type, field_params, field_notes = self.get_field_type(connection, table_name, row)
                    extra_params.update(field_params)
                    comment_notes.extend(field_notes)

                    # Add primary_key and unique, if necessary.
                    if column_name in indexes:
                        if indexes[column_name]['primary_key']:
                            extra_params['primary_key'] = True
                        elif indexes[column_name]['unique']:
                            extra_params['unique'] = True

                    field_type += '('

                # Don't output 'id = meta.AutoField(primary_key=True)', because
                # that's assumed if it doesn't exist.
                if att_name == 'id' and field_type == 'AutoField(' and extra_params == {'primary_key': True}:
                    continue

                # Add 'null' and 'blank', if the 'null_ok' flag was present in the
                # table description.
                if row[6]: # If it's NULL...
                    extra_params['blank'] = True
                    if not field_type in ('TextField(', 'CharField('):
                        extra_params['null'] = True

                field_desc = '%s = models.%s' % (att_name, field_type)
                if extra_params:
                    if not field_desc.endswith('('):
                        field_desc += ', '
                    field_desc += ', '.join(['%s=%r' % (k, v) for k, v in extra_params.items()])
                field_desc += ')'
                if comment_notes:
                    field_desc += ' # ' + ' '.join(comment_notes)
                runko+=  sisennys + field_desc + "\n"
                runko = runko.replace( "Tupa", "" ) 
            for meta_line in self.get_meta(table_name):
                runko+= sisennys + meta_line + "\n"
            koodi = re.sub(r'(?s)(?<=#gen_legacy_class '+ luokka +'\n).*?#end_legacy_class',
                                runko+"\n"+sisennys +r"#end_legacy_class",koodi)
            
        return koodi 

    def get_field_type(self, connection, table_name, row):
        """
        Given the database connection, the table name, and the cursor row
        description, this routine will return the given field type name, as
        well as any additional keyword parameters and notes for the field.
        """
        field_params = {}
        field_notes = []

        try:
            field_type = connection.introspection.get_field_type(row[1], row)
        except KeyError:
            field_type = 'TextField'
            field_notes.append('This field type is a guess.')

        # This is a hook for DATA_TYPES_REVERSE to return a tuple of
        # (field_type, field_params_dict).
        if type(field_type) is tuple:
            field_type, new_params = field_type
            field_params.update(new_params)

        # Add max_length for all CharFields.
        if field_type == 'CharField' and row[3]:
            field_params['max_length'] = row[3]

        if field_type == 'DecimalField':
            field_params['max_digits'] = row[4]
            field_params['decimal_places'] = row[5]

        return field_type, field_params, field_notes

    def get_meta(self, table_name):
        """
        Return a sequence comprising the lines of code necessary
        to construct the inner Meta class for the model corresponding
        to the given database table name.
        """
        return ['class Meta:',
                '    db_table = %r' % table_name,
                '']
