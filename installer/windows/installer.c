#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <stdio.h>
#include <conio.h>


int getconf(char *filename,char **keys,char **values,int max_str_len) ; // function for getting values from config files

void getString(char *string) { // Function for getting raw line input from user
	char ch;
	while ((ch = getchar()) != '\n') {
		if(ch=='\b' && strlen(string) ) string[strlen(string)-1]=0 ;
		else {
			string[strlen(string)]=ch  ;
			string[strlen(string)+1]=0 ;
		}
	}
}

int main(int argc, char** argv) {
	char apachedir[256]="";
	// Luetaan Konffitiedosto
	char defaultdir[256] ;
	char apache_installer[256] ;
	char apache_dir_key[256] ;
	char apache_dir_64key[256] ;
	char apache_dir_value[256] ;
	char program_name[256] ;
	char media_destination[256] ;
	char media_dir[256] ;
	char advanced_apache_installer[256] ;
	char *keys[] = {"default_dir",
			"apache_installer",
			"apache_dir_key",
			"apache_dir_64key",
			"apache_dir_value",
			"program_name",
			"media_destination",
			"media_dir",
			"advanced_apache_installer",
			NULL} ;
	char *values[9] ;
	values[0]=defaultdir ;
	values[1]=apache_installer ;
	values[2]=apache_dir_key ;
	values[3]=apache_dir_64key ;
	values[4]=apache_dir_value ;
	values[5]=program_name ;
	values[6]=media_destination ;
	values[7]=media_dir ;
	values[8]=advanced_apache_installer ;
	getconf("install.cfg",keys,values,256) ;
	
	// Haetaan program files muuttuja :
	char installdir[256]="" ;
	char *program_files ;
	program_files=getenv("ProgramFiles") ;
	strcpy(installdir,program_files) ;
	strcat(installdir,"\\") ;
	strcat(installdir,defaultdir) ;
	
	printf("\nTervetuloa kipan asennusohjelmaan.\n") ;
	char asennus[256] = "" ;
	while( asennus[0]!='1' && asennus[0]!='2' ){
		asennus[0] = 0 ;
		printf("\nValitse asennuksen tyyppi.\n 1) Helppo \n 2) Muokautettu \n\n >>" ) ;
		getString(asennus) ;
	}
	
	// Kysellään tyhmiä:
	printf("\nMihin hakemistoon %s asennetaan? (Oletus=%s)\n Jos oletuspaikka on ok, paina vaan enter. \n\n>>", program_name,installdir) ;
	char hakemisto[256]="";
	getString(hakemisto) ;
	
	
	printf("Asennetaan apache.\n") ;
	// Ajetaan apache asentaja
	if( asennus[0]=='2') system(advanced_apache_installer); 
	else system( apache_installer) ;

	printf("Asennetaan kipa.\n");

	// Ronkitaan rekisteristä,tai kysytään käyttäjältä, apachen asennus hakemisto.
	HKEY hkey;
	unsigned long datalen; 
	unsigned long datatype;
	if (!RegOpenKeyExA(HKEY_LOCAL_MACHINE,
			apache_dir_key,
			NULL,
			KEY_QUERY_VALUE, 
			&hkey) == ERROR_SUCCESS) // Normal windows
	{
		if  (!RegOpenKeyExA(HKEY_LOCAL_MACHINE,
			apache_dir_64key,
			NULL,
			KEY_QUERY_VALUE, 
			&hkey) == ERROR_SUCCESS) // 64 bit windows 7
		{
			printf("\nAsennus ei löytänyt Apachea rekisteristä.\n Kerro Apachen siainti koneellasi \n (Hakemisto jonka alla on suoraan \"modules\" ja \"bin\" hakemisto):\n");
			getString(apachedir) ;
		}
	}
	datalen = 256;
	if (RegQueryValueExA(hkey,
		apache_dir_value ,
		NULL,
		&datatype,
		apachedir,
		&datalen) != ERROR_SUCCESS && !apachedir[0])	
	{
		printf("\nAsennus ei löytänyt Apachea rekisteristä.\nKerro Apachen siainti koneellasi. \n (Hakemisto on se jonka alla on suoraan \"modules\" ja \"bin\" hakemistot):\n");
		getString(apachedir) ;
	}
	RegCloseKey(hkey);
	
	// Toistetaan itsestäänselvyys:
	printf("Apache on hakemistossa:%s\n",apachedir);
	
	if (hakemisto[0]) {
		installdir[0]=0 ;
		strcpy(installdir , hakemisto) ;
	}	


	int i;
	for( i =0 ; i< strlen(installdir) ; i++ ) { // korvataan kaikki /
		 
		if (installdir[i]==47) installdir[i]='\\' ;
	}
	if (installdir[strlen(installdir)-1]=='\\' ) installdir[strlen(installdir)-1]= 0 ; 
	printf("Asennetaan %s hakemistoon \"%s\n\"" , program_name ,installdir) ;

	// Kopioidaan tiedostoja:
	char p_kom[256];
	sprintf(p_kom,"xcopy python\\* \"%s\\python\" /s /y /i /R",installdir );
	char db_bak[256];
	sprintf(db_bak,"xcopy \"%s\\web\\*.db\" \"%s\\web\\bak\\\" /y",installdir, installdir );
	char db_res[256] ;
	sprintf(db_res,"xcopy \"%s\\web\\bak\\*.db\" \"%s\\web\\\" /y",installdir, installdir );
	char w_kom[256];
	sprintf(w_kom,"xcopy web\\* \"%s\\web\" /s /i /y /R",installdir );
	char a_kom[256];
	sprintf(a_kom,"xcopy apache\\* \"%s\" /s /i /y /R",apachedir );
	
	
	// Paivitetaan pythonpath
	char pyPath[256];
	sprintf(pyPath,"%s\\python;%s\\python\\lib;%s\\python\\DLLs;%s\\python\\plat-win;%s\\python\\lib\\lib-tk",installdir,installdir,installdir,installdir,installdir);
	if (!RegOpenKeyExA(HKEY_LOCAL_MACHINE,
			"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
			NULL,
			KEY_SET_VALUE, 
			&hkey) == ERROR_SUCCESS)
	{
		printf("Ei onnistu laittamaan python pathia.\n Kokeile ajaa uudestaan admin oikeuksilla.");
		while( !kbhit());
		return -1 ;
	}
	datalen = 256;
	RegSetValueEx(
  		hkey,
 		"PythonPath",
  		0,
  		REG_EXPAND_SZ,
  		pyPath,
  		255);
	RegCloseKey(hkey);

	// Nollataan apachen konfigurointitiedosto. Ettei päivitettäessä kumuloidu. 
	char ht_kom[256];
	sprintf(ht_kom ,"copy \"%s\\conf\\original\\httpd.conf\" \"%s\\conf\\\"", apachedir,apachedir) ;

	system( p_kom );
        system( db_bak ) ;	
	system( w_kom ); 
	system( db_res ) ;
	system( a_kom ); 
	system( ht_kom ); 

	// Paivitetaan httpd.conf
	
	char httpd_conf[512] ;
	sprintf(httpd_conf,"Alias %s \"%s\\web\\%s\" \n <Directory \"%s\\web\\%s\"> \n Order allow,deny \n  Allow from all \n </Directory> \n LoadModule python_module modules/mod_python.so \n <Location \"/%s/\"> \n SetHandler python-program \n PythonHandler django.core.handlers.modpython \n SetEnv DJANGO_SETTINGS_MODULE web.settings \n PythonDebug On \n PythonPath \"['%s'] + sys.path\" \n </Location> \n",media_destination,
										 installdir,
										 media_dir,
										 installdir,
										 media_dir,
										 program_name,
										 installdir) ; 
	
	char httpd_filename[256] ;
	sprintf(httpd_filename,"%s\\conf\\httpd.conf",apachedir) ;

	FILE *fp;
	fp = fopen(httpd_filename, "a");
	for (i=0; i<strlen(httpd_conf); i++ ) { 
		fputc( httpd_conf[i], fp );
	}
	fclose(fp);


	
	// Käynnistetään apache uudestaan
	char httpd_stop[255] ; sprintf(httpd_stop,"\"%s\\bin\\httpd.exe\" -k stop",apachedir );
	char httpd_start[255] ; sprintf(httpd_start,"\"%s\\bin\\httpd.exe\" -k start" ,apachedir) ;
	system( httpd_stop ); 
	system( httpd_start ); 
	
	printf("\nAsennus on valmis! \n \nJotkin systeemit tarvitsevat koneen rebootin (Windows XP) \n");
        printf("\nKipa on web selaimella osoitteessa: http://localhost/kipa/ \n\nPaina jotain nappia lopettaaksesi.");
	while( !kbhit());
	// Käynistetään selain
	//
	char browser[256];
	sprintf(browser, "START /B http://localhost/%s/", program_name );
	system( browser ); 
	return 0 ;
}


/* Arguments:
 * char *filename cofig file name
 * char **keys NULL terminated array of key strings to extracted from config file.
 * char **values array for the key values 
 * int max_str_len max size of config file line
*/
int getconf(char *filename,char **keys,char **values,int max_str_len) {
	char s[255];
	int i;
	FILE *f ;
	f = fopen("install.cfg", "r");
	if( !f ) {
		printf("Error! No install.cfg found, exiting.\n") ;
		return 0;
	}
	i=0;
	while( keys[i] ) {
		values[i][0]=0;
		i+=1;
	}
	while(  fgets( s, max_str_len, f )) {
		char *arg  ;
		char *value ;
		arg =(char*) malloc(max_str_len) ;
		value = (char*) malloc(max_str_len) ;
		arg[0]=0;	
		value[0]=0;
		value[max_str_len-1] = 0;
		arg[max_str_len-1] = 0;
		int split=0;
		for(i=0 ; i<max_str_len ; i++) {
			if(split){
				value[i-split-1] = s[i];
				if(s[i]=='#' || !s[i] || s[i]=='\n' ) {
					value[i-split-1]=0;
					break ;
				}
			}
			else {
				arg[i]=s[i];
				if(s[i]=='=') {
					split=i;
					arg[i]=0;
				}
				if(s[i]=='#' || !s[i]) {
					value[0]=0;
					arg[i]=0 ;
					break ;
				}
			}
		}
		// remove whitespace
		while (strlen(arg) && arg[strlen(arg)-1] ==' ' ) arg[strlen(arg)-1]=0 ;
		while (strlen(value) && value[strlen(value)-1]==' ' ) value[strlen(value)-1]=0 ;
		if( value[0] && arg[0] ) {
			i=0;
			while( keys[i] ) {
				if (strcmp(keys[i] , arg )==0 ){
					int alku=0 ;
					while (value[alku]==' ' ) alku+=1 ;

					if (value[0]== ' ') strcpy( values[i] , value+alku ) ;	
				}
				i=i+1;
			}
		}
		
		free(arg);
		free(value);
	}
	return 1 ;
}

