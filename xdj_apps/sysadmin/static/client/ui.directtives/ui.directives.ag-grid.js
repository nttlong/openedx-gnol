/*
    <div b-ag-grid  
        id="agGrid" 
        on-load-data="doLoadData" 
        data-allow-edit="false" 
        data-show-selected-column="true"
        data-on-before-edit="showBeforeEdit"
        data-selected-row="selectedRow"
        data-on-edit="doEditWithRow(myRow)"
        data-on-insert="doInsert()"
        data-on-delete="doDelete(myRow)"
        data-msg-delete="Do you want to delete this row?"
        data-row="myRow"
        data-dialog-ok-caption="OK"
        data-dialog-cancel-caption="Cancel"
        data-dialog-message-content ="Do you want to delete"
        data-dialog-caption="Confirm message"

        >
        <columns>
            
            <column data-field='code' data-width='200' title="${get_app_res('Code')}" data-pinned="left"></column>
            <column data-field='name' title="${get_app_res('Name')}"></column>
            <column data-field='description' title="${get_app_res('Description')}"></column>
            <column data-field='created_on' title="${get_app_res('Created on')}" data-width="100" data-type='date'></column>
            <column data-field='created_by' title="${get_app_res('Created by')}" data-width="200"></column>
        </columns>
    </div>
*/

var ag_grid_msg_delete_dialog ='<div class="modal" tabindex="-1" role="dialog">'+
  '<div class="modal-dialog" role="document">'+
   ' <div class="modal-content">'+
    '  <div class="modal-header">'+
    '    <h5 class="modal-title" id="dialogTitle">Comfirm message</h5>'+
    '   <button type="button" class="close" data-dismiss="modal" aria-label="Close">'+
    '     <span aria-hidden="true">&times;</span>'+
    '   </button>'+
    ' </div>'+
    ' <div class="modal-body">'+
    '   <p id="dialogContent">Do you want to delete this row?</p>'+
    ' </div>'+
    
    ' <div class="modal-footer">'+
    //'<p>Do not show this message on the next time</p>'+
    '   <button type="button" class="btn btn-primary" id="dialogBtnOK">OK</button>'+
    '   <button type="button" class="btn btn-secondary" data-dismiss="modal" id="dialogBtnClose">Cancel</button>'+
    ' </div>'+
    '</div>'+
    '</div>'+
  '</div>';

  angularDefine(function(mdl){
    mdl.directive('bAgGrid', ["$parse","$filter", function ($parse,$filter) {
       
        
        return {
        restrict: "CEA",
        replace: true,
        transclude:true,
        template:"<div><div id='grid' style='height:400px'></div><div  ng-transclude style='display:none' id='configs'></div></div>" ,
        link: function (scope, ele, attr) {
            var agGrid;
            function watch(){
                
                if(window.agGrid && typeof window.agGrid==="object" && window.agGrid.Grid){
                    agGrid=window.agGrid;
                    //agGrid.initialiseAgGridWithAngular1(angular);
                    init();
                }
                else {
                    setTimeout(watch,1);
                }
            }
            
            function init(){
                
                var cmp = new function(){
                    var me=this;
                    me.api=undefined;
                    me.grid=undefined;
                    me.currentCell=undefined;
                    me.currentSelectedRowIndex=undefined;
                    me.currentSelectedEle=undefined;
                    me.row=undefined;
                    me.focus=function(){
                        if(me.currentCell){
                            me.api.setFocusedCell(me.currentCell.rowIndex, me.currentCell.column.colId);
                        }
                        else {
                            me.api.setFocusedCell(0, gridOptions.colDef[0].field);
                        }
                    }
                }
                function fireOnRowEdit(data){
                    if(attr.row){
                        $parse(attr.row).assign(scope,data);
                    }
                    cmp.row = data;
                    if(attr.onEdit){
                        var fn =scope.$eval(attr.onEdit);
                        if(angular.isFunction(fn)){
                            fn(data);
                        }
                    }
                }
                function fireOnAddNewRow(){
                    if(attr.onInsert){
                        var fn =scope.$eval(attr.onInsert);
                        if(angular.isFunction(fn)){
                            fn();
                        }
                    }
                }
                function showDalog(action){
                    var div=$(ag_grid_msg_delete_dialog).appendTo("body");
                    div.find("#dialogBtnOK").click(function(){
                        action();
                        div.find("#dialogBtnClose").trigger("click");
                    })
                    if(attr.dialogOKCaption){
                        div.find("#dialogBtnOK").html(attr.dialogOKCaption)
                    }
                    else {
                        if(scope.$root.$settings && 
                            scope.$root.$settings.$confirmDeleteDialog && 
                            scope.$root.$settings.$confirmDeleteDialog.okCaption){
                                div.find("#dialogBtnOK").html(scope.$root.$settings.$confirmDeleteDialog.okCaption)
                            }
                        else {
                            console.warn("You should put '$settings.$confirmDeleteDialog.okCaption' at root scope")
                        }
                    }
                    if(attr.dialogCancelCaption){
                        div.find("#dialogBtnClose").html(attr.dialogCancelCaption)
                    }
                    else {
                        if(scope.$root.$settings && 
                            scope.$root.$settings.$confirmDeleteDialog && 
                            scope.$root.$settings.$confirmDeleteDialog.cancelCaption){
                                div.find("#dialogBtnOK").html(scope.$root.$settings.$confirmDeleteDialog.cancelCaption)
                            }
                        else {
                            console.warn("You should put '$settings.$confirmDeleteDialog.cancelCaption' at root scope")
                        }
                    }
                    if(attr.dialogMessageContent){
                        div.find("#dialogContent").html(attr.dialogMessageContent)
                    }
                    else {
                        if(scope.$root.$settings && 
                            scope.$root.$settings.$confirmDeleteDialog && 
                            scope.$root.$settings.$confirmDeleteDialog.message){
                                div.find("#dialogBtnOK").html(scope.$root.$settings.$confirmDeleteDialog.message)
                            }
                        else {
                            console.warn("You should put '$settings.$confirmDeleteDialog.message' at root scope")
                        }
                    }
                    if(attr.dialogCaption){
                        div.find("#dialogTitle").html(attr.dialogCaption)
                    }
                    else {
                        if(scope.$root.$settings && 
                            scope.$root.$settings.$confirmDeleteDialog && 
                            scope.$root.$settings.$confirmDeleteDialog.title){
                                div.find("#dialogBtnOK").html(scope.$root.$settings.$confirmDeleteDialog.title)
                            }
                        else {
                            console.warn("You should put '$settings.$confirmDeleteDialog.title' at root scope")
                        }
                    }
                    div.on("shown.bs.modal", function () { 
                        setTimeout(function(){
                            div.find("#dialogBtnOK").focus();
                        },500);
                        
                    }).on('hide.bs.modal',function(){
                        setTimeout(function(){
                            cmp.focus();
                        },300);
                        
                    }).modal();
                }
                function fireOnRowDelete(data){
                    if(attr.row){
                        $parse(attr.row).assign(scope,data);
                    }
                    cmp.row = data;
                    if(attr.onDelete){
                        showDalog(function(){
                            var fn =scope.$eval(attr.onDelete);
                            if(angular.isFunction(fn)){
                                fn(data);
                            }
                        });
                        
                    }
                }
                cmp.doEdit=function(){
                    fireOnRowEdit(cmp.row)
                }
                cmp.doDelete=function(){
                    fireOnRowDelete(cmp.row)
                }
                cmp.doInsert=function(){
                    fireOnAddNewRow(cmp.row)
                }
                cmp.doRefresh=function(){
                    cmp.datasource.getRows(cmp.postParams);
                }
                function hookKeyDown(event){
                    var isInGrid=$.contains(ele.find(".ag-body")[0],event.target);
                    if(!isInGrid) return;
                    if(event.keyCode!=13 &&
                    event.keyCode !=45 &&
                    event.keyCode != 46 &&
                    event.keyCode != 116
                    ){
                        return;
                    } 
                    if(event.keyCode==13){
                        if(attr.allowEdit=="true") return;
                        if(cmp.currentSelectedRowIndex ==null) return;
                            if(cmp.api ==null) return;
                        
                            cmp.api.selectIndex(cmp.currentSelectedRowIndex)
                                var row=cmp.api.getSelectedRows();
                                if(attr.selectedRow){
                                    $parse(attr.selectedRow).assign(scope,row);
                                    scope.$applyAsync();
                                };
                        fireOnRowEdit(row[0]);
                    }
                    if(event.keyCode==46){
                        if(attr.allowEdit=="true") return;
                        cmp.currentCell =cmp.api.getFocusedCell();
                        cmp.currentSelectedEle=event.target;
                        if(cmp.currentSelectedRowIndex ==null) return;
                            if(cmp.api ==null) return;
                        
                            cmp.api.selectIndex(cmp.currentSelectedRowIndex)
                                var row=cmp.api.getSelectedRows();
                                if(attr.selectedRow){
                                    $parse(attr.selectedRow).assign(scope,row);
                                    scope.$applyAsync();
                                };
                            fireOnRowDelete(row[0]);
                    }
                    if(event.keyCode==45){
                        if(attr.allowEdit=="true") return;
                        fireOnAddNewRow();

                    }
                    if(event.keyCode==116){
                        cmp.datasource.getRows(cmp.postParams);
                    }

                    event.preventDefault();
                    
                    
                }
                function unHookGridKeyDownWatcher(){
                    if(!$.contains($("body")[0],ele[0])){
                        $(window).unbind("keydown",hookKeyDown);
                        
                        delete unHookGridKeyDownWatcher;
                    }
                    else {
                        setTimeout(unHookGridKeyDownWatcher,100);
                    }
                    
                }
                function hookGridKeyDownWatcher(){
                    if($.contains($("body")[0],ele[0])){
                        $(window).bind("keydown",hookKeyDown);
                        delete hookGridKeyDownWatcher;
                    }
                    else {
                        setTimeout(hookGridKeyDownWatcher,100);
                    }
                    
                }
                var gEle=undefined;
                if(attr.id){
                    $parse(attr.id).assign(scope,cmp);
                }
                var dataSource = {
                    rowCount: null,
                    getRows: function (params) {
                        cmp.postParams=params;
                        pageIndex=params.endRow/100 -1;
                        if(attr.onLoadData){
                            var fn= scope.$eval(attr.onLoadData);
                            if(angular.isFunction(fn)){
                                var sender = {
                                    params:{
                                        filter:params.filterModel,
                                        sort:params.sortModel,
                                        pageIndex:pageIndex,
                                        pageSize:params.endRow-params.startRow,
                                    },
                                    done:function(res){
                                        params.successCallback(res.items, res.total_items);
                                    }
                                }
                                fn(sender)
                            }
                        }
                    }
                };
                cmp.datasource=dataSource;
                var gridOptions = {
                    columnDefs: [],
                    enableServerSideFilter: true,
                    floatingFilter:false,
                    enableServerSideSorting: true,
                    enableColResize: true,
                    rowBuffer: 0,
                    debug: true,
                    rowSelection: 'multiple',
                    rowDeselection: true,
                    rowModelType: 'infinite',
                    paginationPageSize: 20,
                    cacheOverflowSize: 2,
                    maxConcurrentDatasourceRequests: 2,
                    infiniteInitialRowCount: 1,
                    maxBlocksInCache: 2,
                    onGridReady: function(params) {
                        unHookGridKeyDownWatcher();
                        hookGridKeyDownWatcher();
                        setTimeout(function(){params.api.sizeColumnsToFit();},200)
                        // params.api.sizeColumnsToFit();
                        params.api.setDatasource(dataSource);
                        cmp.api =params.api;

                       
                        var h=ele.height();
                        function watchHeight(){
                            var r=ele.height()
                            if(h!=r){
                                h=r;
                                fixHeight(r);

                            }
                            setTimeout(watchHeight,100);
                        }
                        function fixHeight(r){
                            var gEle=ele.find(".ag-theme-fresh");
                            if(gEle){
                            gEle.css({
                                    height:r
                                })
                            }


                            // params.api.sizeColumnsToFit();
                        }
                        fixHeight(ele.height());
                        watchHeight();
                        window.addEventListener('resize', function() {
                            setTimeout(function() {
                            //   params.api.sizeColumnsToFit();
                            })
                        })
                    },
                    onCellFocused:function(event){

                        if(event.rowIndex==null) return;
                        cmp.currentCell =event.api.getFocusedCell();
                        cmp.currentSelectedRowIndex =event.rowIndex;
                    },
                    onCellEditingStarted: function(event) {
                        var row=event.api.getSelectedRows()[0];
                        cmp.row=row;
                        if(attr.row){
                            $parse(attr.row).assign(scope,row);
                            scope.$applyAsync();
                        }
                        if (attr.onBeforeEdit){
                            var fn=scope.$eval(attr.onBeforeEdit);
                            if(angular.isFunction(fn)){
                                fn(event.data,event.column.colDef.field);
                            }
                        }
                    },
                    onCellEditingStopped: function(event) {
                        if (attr.onAfterEdit){
                            var fn=scope.$eval(attr.onAfterEdit);
                            if(angular.isFunction(fn)){
                                fn(event.data,event.column.colDef.field);
                            }
                        }
                    },
                    onSelectionChanged: function(event){
                        var row=event.api.getSelectedRows()[0];
                        cmp.row=row;
                        if(attr.row){
                            $parse(attr.selectedRow).assign(scope,row);
                            scope.$applyAsync();
                        }
                    },
                    onCellDoubleClicked:function(event){
                        var row=event.api.getSelectedRows()[0];
                        cmp.row=row;
                        if(attr.row){
                            $parse(attr.row).assign(scope,row);
                            scope.$applyAsync();
                        }

                        if(attr.allowEdit=="true") return;
                        fireOnRowEdit(event.data);
                    }
                };
                function cleanGrid(){
                    $(ele.find("#grid")[0]).empty();
                }
                function agBComponentEditor(){
                }
                agBComponentEditor.prototype.init=function(params){
                    if(params.column.colDef.$$$component){
                        this.eInput= params.column.colDef.$$$component;
                        return;
                    }
                    var componentId=params.column.colDef.$$data_component;
                    this.eInput=ele.find("components").find("#"+componentId).children()[0];
                    this.componentId=componentId;
                    params.column.colDef.$$$component=this.eInput;
                }
                agBComponentEditor.prototype.getGui=function(){
                    return this.eInput;
                }
                agBComponentEditor.prototype.getValue=function(){
                    return"XXX";
                }
                agBComponentEditor.prototype.isPopup = function () {
                    // and we could leave this method out also, false is the default
                    return true;
                };
                agBComponentEditor.prototype.afterGuiAttached = function () {
                    $(this.eInput).find("input")[0].focus();
                };
                agBComponentEditor.destroy = function () {
                    $(this.eInput).appendTo(ele.find("components").find("#"+componentId)[0]);
                    // but this example is simple, no cleanup, we could  even leave this method out as it's optional
                };
                /** create columns */
                function createColumnsFromColsEles(elem){
                    var ret =[];
                    var autoWidthCols =[];
                    var totalWidth =0;
                    if(attr.showSelectedColumn){
                        col={
                            displayName:"<input type=\"checkbox\">",
                            field:"$selected"
                        }
                        col.width=50;
                        col.minWidth=50;
                        col.maxWidth=50;
                        totalWidth+=col.width;
                        col.suppressMenu=true;
                        col.suppressSorting = true;
                        col.cellRenderer=function(params){
                            if(params.value){
                                return "<input type=\"checkbox\" checked=\"checked\">"
                            }
                            else {
                                return "<input type=\"checkbox\">"
                            }
                        }
                        ret.push(col);
                    }
                    elem.children().each(function(idx,e){
                        var col= {
                            headerName:$(e).attr('title'),
                            field:$(e).attr('data-field'),
                        }
                        col.editable=false;
                        if($(e).attr("data-component")){
                            col.$$data_component=$(e).attr("data-component");
                            col.cellRenderer=function(params){
                                return params.value;

                            }
                            col.cellEditor='componentEditor';
                            
                            if(!gridOptions.components){
                                gridOptions.components={
                                    componentEditor:agBComponentEditor
                                }
                            }
                        }
                        if(attr.allowEdit=="true"){
                        if( $(ele).attr('data-editable') !='true'){
                                col.editable=true;
                            }
                        }
                        if($(e).attr('data-width')){
                            col.width =$(e).attr('data-width')*1
                            totalWidth+=col.width;
                            //col.maxWidth =$(e).attr('data-width')*1
                        }
                        else if ($(e).attr("data-cell-type")=='checkbox'){
                            col.width=40;
                            col.minWidth=40;
                            col.maxWidth=40;
                            totalWidth+=col.width;
                            col.suppressMenu=true;
                            col.suppressSorting = true;
                            col.cellRenderer=function(params){
                                if(params.value){
                                    return "<input type=\"checkbox\" checked=\"checked\">"
                                }
                                else {
                                    return "<input type=\"checkbox\">"
                                }
                            }
                        }
                        else {
                            autoWidthCols.push(col)
                        }
                        if($(e).attr("data-lock")=="true"){
                            col.lockPosition=true;
                        }
                        if($(e).attr("data-pinned")){
                            col.pinned=$(e).attr("data-pinned");
                        }
                        if($(e).attr('data-type')=='date'){
                            col.cellRenderer=function(params){
                                if($(e).attr('data-format')){
                                    return $filter("date")(params.value,$(e).attr('data-format'));
                                }
                                else {
                                    if(scope.$root.$settings && scope.$root.$settings.defaultDateFormat){
                                        return $filter("date")(params.value,scope.$root.$settings.defaultDateFormat);
                                    }
                                    else {
                                        return "root scope with defaultDateFormat in $settings was not found, please put $settings.defaultDateFormat at root scope";
                                    }
                                }
                            }
                        }
                        ret.push(col)
                    });
                    var gridWidth = $(ele).width();
                    if(autoWidthCols.length>0){
                        var mWidth =gridWidth-totalWidth-15;
                        if(mWidth>0){
                            var nWidth= mWidth/autoWidthCols.length;
                            for(var i=0;i<autoWidthCols.length;i++){
                                autoWidthCols[i].width=nWidth;
                            }
                        }
                    }
                    return ret;
                }
                attr.$observe("columns",function(val){
                    var cols =scope.$eval(val);
                    if(angular.isUndefined(cols)) {
                        return
                    }
                    gridOptions.columnDefs =cols;
                    gridOptions.height=$(ele[0]).height();
                    $(ele.find("#grid")[0]).empty();
                    gEle=$("<div  class=\"ag-theme-fresh\"></div>")
                    gEle.appendTo(ele.find("#grid")[0]);
                   
                    cmp.grid =new agGrid.Grid(gEle[0], gridOptions);
                    if(attr.id){
                        $parse(attr.id).assign(scope,cmp);
                    }


                })
                
                scope.$watch(function(){
                    return ele.find('#configs').find('columns').html()
                },function(o,v){
                    var cols=createColumnsFromColsEles(ele.find('#configs').find('columns'))
                    gridOptions.columnDefs =cols;
                    gridOptions.height=$(ele[0]).height();
                    $(ele.find("#grid")[0]).empty();
                    var gEle=$("<div  class=\"ag-theme-fresh\" ></div>").appendTo(ele.find("#grid")[0]);
                    // gEle.css({
                    //     height:$(ele.height())
                    // });
                    cmp.grid =new agGrid.Grid(gEle[0], gridOptions);
                    if(attr.id){
                        $parse(attr.id).assign(scope,cmp);
                    }

                })
             }
             watch();
        }
    }}]);
  })

