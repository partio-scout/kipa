/*
 * jQuery columnHover plugin
 * Version: 0.1.1
 *
 * Copyright (c) 2007 Roman Weich
 * http://p.sohei.org
 *
 * Dual licensed under the MIT and GPL licenses 
 * (This means that you can choose the license that best suits your project, and use it accordingly):
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Changelog: 
 * v 0.1.1 - 2007-08-05
 *	-change: included new option "ignoreCols", through which columns can be excluded from the highlighting process
 * v 0.1.0 - 2007-05-25
 */

(function($)
{
	/**
	 * Calculates the actual cellIndex value of all cells in the table and stores it in the realCell property of each cell.
	 * Thats done because the cellIndex value isn't correct when colspans or rowspans are used.
	 * Originally created by Matt Kruse for his table library - Big Thanks! (see http://www.javascripttoolbox.com/)
	 * @param {element} table	The table element.
	 */
	var fixCellIndexes = function(table) 
	{
		var rows = table.rows;
		var len = rows.length;
		var matrix = [];
		for ( var i = 0; i < len; i++ )
		{
			var cells = rows[i].cells;
			var clen = cells.length;
			for ( var j = 0; j < clen; j++ )
			{
				var c = cells[j];
				var rowSpan = c.rowSpan || 1;
				var colSpan = c.colSpan || 1;
				var firstAvailCol = -1;
				if ( !matrix[i] )
				{ 
					matrix[i] = []; 
				}
				var m = matrix[i];
				// Find first available column in the first row
				while ( m[++firstAvailCol] ) {}
				c.realIndex = firstAvailCol;
				for ( var k = i; k < i + rowSpan; k++ )
				{
					if ( !matrix[k] )
					{ 
						matrix[k] = []; 
					}
					var matrixrow = matrix[k];
					for ( var l = firstAvailCol; l < firstAvailCol + colSpan; l++ )
					{
						matrixrow[l] = 1;
					}
				}
			}
		}
	};

	/**
	 * Highlight whole table columns when hovering over a table.
	 * Works on tables with rowspans and colspans.
	 *
	 * @param {map} options			An object for optional settings (options described below).
	 *
	 * @option {string} hoverClass		A CSS class that is set on the cells in the column with the mouse over.
	 *							Default value: 'hover'
	 * @option {boolean} eachCell		Allows highlighting the column while hovering over the table body or table footer. When disabled, highlighting is allowed only through the table header.
	 *							Default value: false
	 * @option {boolean} includeSpans		Includes columns with the colspan attribute set in the hover and highlight process.
	 *							Default value: true
	 * @option {array} ignoreCols		An array of numbers. Each column with the matching column index won't be included in the highlighting process.
	 *							Index starting at 1!
	 *							Default value: [] (empty array)
	 *
	 * @example $('#table').columnHover();
	 * @desc Allow column hovering/highlighting for the table using the default settings.
	 *
	 * @example $('#table').columnHover({eachCell:true, hoverClass:'someclass'});
	 * @desc Allow column hovering/highlighting for the whole table (including the body and footer). Set the class "someclass" to the cells in the column with the mouse over.
	 *
	 * @type jQuery
	 *
	 * @name columnHover
	 * @cat Plugins/columnHover
	 * @author Roman Weich (http://p.sohei.org)
	 */
	$.fn.columnHover = function(options)
	{
		var settings = $.extend({
				hoverClass: 'hover',
				eachCell: false,
				includeSpans : true,
				ignoreCols : []
			}, options);

		/**
		 * Adds or removes the hover style on the column.
		 * @param {element} cell	The cell with the mouseover/mouseout event.
		 * @param {array} colIndex	The index with the stored columns.
		 * @param {boolean} on		Defines whether the style will be set or removed.
		 */
		var hover = function(cell, colIndex, on)
		{
			var a = colIndex[cell.realIndex];
			var i = 0;
			if ( $(settings.ignoreCols).index(cell.realIndex + 1) != -1 )
			{
				return; //dont highlight the columns in the ignoreCols array
			}
			while ( ++i < cell.colSpan )
			{
				a = a.concat(colIndex[cell.realIndex + i]);
			}
			if ( on )
			{
				$(a).addClass(settings.hoverClass);
			}
			else
			{
				$(a).removeClass(settings.hoverClass);
			}
		};

		/**
		 * Adds the hover events to the cell.
		 * @param {jQuery result array} $s	The elements to add the events to.
		 * @param {array} colIndex	The index with the stored columns.
		 */
		var addHover = function($s, colIndex)
		{
			$s.bind('mouseover', function(){
				hover(this, colIndex, true);
			}).bind('mouseout', function(){
				hover(this, colIndex, false);
			});
		};
		
		return this.each(function() 
        {
			var colIndex = [];
			var tbl = this;
			var body, row, c, tboI, rowI, cI, rI, s;

			if ( !tbl.tBodies || !tbl.tBodies.length || !tbl.tHead || !settings.hoverClass.length )
			{
				return;
			}
			fixCellIndexes(tbl);
			//create index - loop through the bodies
			for ( tboI = 0; tboI < tbl.tBodies.length; tboI++ )
			{
				body = tbl.tBodies[tboI];
				//loop through the rows
				for ( rowI = 0; rowI < body.rows.length; rowI++ )
				{
					row = body.rows[rowI];
					//each cell
					for ( cI = 0; cI < row.cells.length; cI++ )
					{
						c = row.cells[cI];
						//ignore cells with colspan?
						if ( !settings.includeSpans && c.colSpan > 1 )
						{
							continue;
						}
						s = (settings.includeSpans) ? c.colSpan : 1;
						while ( --s >= 0 )
						{
							rI = c.realIndex + s;
							if ( !colIndex[rI] )
							{
								colIndex[rI] = [];
							}
							colIndex[rI].push(c);
						}
						//add hover event?
						if ( settings.eachCell )
						{
							addHover($(c), colIndex);
						}
					}
				}
			}
			//events
			addHover($('td, th', tbl.tHead), colIndex);
			//add hover event to footer?
			if ( settings.eachCell && tbl.tFoot )
			{
				addHover($('td, th', tbl.tFoot), colIndex);
			}
		});
	};
})(jQuery); 
