
angularDefine(function(mdl){
    mdl.directive("handsOnTable",[function(){
        return {
            restrict:"ECA",
            template:"<div style='border:solid 4px red'></div>",
            replace:true,
            link:function(s,e,a){
                function watch(){
                    if(window.Handsontable){
                        var hot1 = new window.Handsontable(e[0], {
                        data: [],
                        width: 584,
                        height: 320,
                        colWidths: 100,
                        rowHeights: 23,
                        rowHeaders: true,
                        colHeaders: true
                        });
                        delete watch;
                    }
                    else {
                        setTimeout(watch,1);
                    }
                }
                watch();
                

            }
        }
    }])
})