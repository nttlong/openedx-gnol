
function makeUpForm(divRow,a){
   
    // divRow.hide();
   
    var rows=divRow.children();
    for(var x=0;x<rows.length;x++){
        var eles=$(rows[x]).children();
        var tmpDiv=$("<div></div>");

        for(var i=0;i<eles.length;i++){
            var div=$("<div class='form-element'></div>");
            var ele=$(eles[i]);
            if (ele.attr("ng-show")){
                div.attr("ng-show",ele.attr("ng-show"))

            }
            if (ele.attr("ng-if")){
                div.attr("ng-if",ele.attr("ng-if"))

            }
            if((ele[0].tagName==="LABEL")||
            ((ele[0].tagName==="SPAN"))){
                ele.addClass("control-label");
            }
            if((ele[0].tagName==="INPUT")&&
            (((ele[0].type==="text")||
              (ele[0].type==="number")||
              (ele[0].type==="select")||
              (ele[0].type==="email")||
              (ele[0].type==="password")
            ))){
                ele.addClass("form-control");
            }
            if((ele[0].tagName==="INPUT")&&
            (((ele[0].type==="button")||
              (ele[0].type==="submit")
            ))){
                ele.addClass("btn");
            }
            if(ele.attr("span")){
                if(!ele.attr("xs-span")){
                    ele.attr("xs-span",ele.attr("span"))
                }
                if(!ele.attr("sm-span")){
                    ele.attr("sm-span",ele.attr("span"))
                }
                if(!ele.attr("md-span")){
                    ele.attr("md-span",ele.attr("span"))
                }
                if(!ele.attr("lg-span")){
                    ele.attr("lg-span",ele.attr("span"))
                }
            }
            $(eles[i]).appendTo(div[0]);
            div.appendTo(tmpDiv[0]);
        }
        $(rows[x]).addClass("row")
        tmpDiv.contents().appendTo(rows[x]);

    }
    for(var x=0;x<rows.length;x++){
        var eles=$(rows[x]).children();
        var mdCols=(a.mdCols||"3,9").split(',');
        var smCols=(a.smCols||"4,8").split(',');
        var lgCols=(a.lgCols||"2,4,2,4").split(',');
        var xsCols=(a.xsCols||"12").split(',');
        var mdIndex=0;
        var smIndex=0;
        var lgIndex=0;
        var xsIndex=0;

        var mdTotal=0;
        var smTotal=0;
        var lgTotal=0;
        var xsTotal=0;
        for(var i=0;i<eles.length;i++){
            if($($(eles[i]).children()[0]).attr("break")!== undefined){
                console.log(lgTotal);
                var _xs=12-xsTotal %12;
                var _sm=12-smTotal %12;
                var _md=12-mdTotal %12;
                var _lg=12-lgTotal %12;
                $(eles[i]).addClass("col-xs-"+_xs);
                $(eles[i]).addClass("col-sm-"+_sm);
                $(eles[i]).addClass("col-md-"+_md);
                $(eles[i]).addClass("col-lg-"+_lg);
                $(eles[i]).css("border","solid 4px red");
                $(eles[i]).css("clear","right");
                mdIndex=0;
                smIndex=0;
                lgIndex=0;
                xsIndex=0;

                mdTotal=0;
                smTotal=0;
                lgTotal=0;
                xsTotal=0;
            }
            else {
                var xsValue=xsCols[xsIndex]*1;
                if($($(eles[i]).children()[0]).attr("xs-span")){
                    var xsSpanValue=$($(eles[i]).children()[0]).attr("xs-span")*1;
                    for(var j=1;j<xsSpanValue;j++){
                        xsIndex++;
                        if(xsIndex<xsCols.length){
                            xsValue+=xsCols[xsIndex]*1;
                        }
                    }
                }
                xsTotal+=xsValue;
                $(eles[i]).addClass("col-xs-"+xsValue);
                var smValue=smCols[mdIndex]*1;
                if($($(eles[i]).children()[0]).attr("sm-span")){
                    var smSpanValue=$($(eles[i]).children()[0]).attr("sm-span")*1;
                    for(var j=1;j<smSpanValue;j++){
                        smIndex++;
                        if(smIndex<smCols.length){
                            smValue+=smCols[smIndex]*1;
                        }
                    }
                }
                smTotal+=smValue;
                $(eles[i]).addClass("col-sm-"+smValue);
                var mdValue=mdCols[mdIndex]*1;
                if($($(eles[i]).children()[0]).attr("md-span")){
                    var mdSpanValue=$($(eles[i]).children()[0]).attr("md-span")*1;
                    for(var j=1;j<mdSpanValue;j++){
                        mdIndex++;
                        if(mdIndex<mdCols.length){
                            mdValue+=mdCols[mdIndex]*1;
                        }
                    }
                }
                mdTotal+=mdValue;
                $(eles[i]).addClass("col-md-"+ mdValue);
                var lgValue=lgCols[lgIndex]*1;
                if($($(eles[i]).children()[0]).attr("lg-span")){
                    var lgSpanValue=$($(eles[i]).children()[0]).attr("lg-span")*1;
                    for(var j=1;j<lgSpanValue;j++){
                        lgIndex++;
                        if(lgIndex<lgCols.length){
                            lgValue+=lgCols[lgIndex]*1;
                        }
                    }
                }
                lgTotal+=lgValue;
                $(eles[i]).addClass("col-lg-"+lgValue);
                if(mdIndex+1<mdCols.length){
                    mdIndex++;
                }
                else {
                    mdIndex=0;
                }
                if(smIndex+1<smCols.length){
                    smIndex++;
                }
                else {
                    smIndex=0;
                }
                if(lgIndex+1<lgCols.length){
                    lgIndex++;
                }
                else {
                    lgIndex=0;
                }
                if(xsIndex+1<xsCols.length){
                    xsIndex++;
                }
                else {
                    xsIndex=0;
                }
            }

        }
    }
    return divRow;
}
angularDefine(function(mdl){
    mdl.directive("formData",["$parse","$compile",function($parse,$compile){
    return {
    restrict:"ECA",
    transclude:true,
    priority:0,
    template:"<div ng-transclude></div>",
    replace:true,
    link:function(s,e,a){


    function watch(){
        if(e.attr("data-template")){
            init(decodeURIComponent(e.attr("data-template")));
            e.removeAttr("data-template");
        }
        else {
            setTimeout(watch,10);
        }    
    }
    function init(html){
    
        var subScope = s.$new();
        subScope.data=s.$eval(a.source);
        s.$watch(a.source,function(o,v){
            console.log(v);
            subScope._=o;
            subScope.$applyAsync();

        })
        var divRow=$("<div></div>");
        divRow.html(html);
        $compile(divRow.contents())(subScope);
        divRow=makeUpForm(divRow,a);
        
        divRow.contents().appendTo(e[0])

        s.$apply();
    }
    watch();
    }
    }
    }]);
    mdl.directive("formTemplate",[function(){
    return {
        restrict:"ECA",
        scope:false,
        compile: function(element, attributes){
            var originHtml=element.html();
            element.empty();
            return {
                pre: function(s, e, a, c, t){
                e.parent().attr("data-template",encodeURIComponent(originHtml));
                    e.remove();
                    
                },
                post: function(s, e, a, c, t){
                
                }
            }
         }
        }
    }]);
    mdl.directive("formLayout",["$parse","$compile",function($parse,$compile){
        return {
            restrict:"ECA",
            template:"<div ng-transclude></div>",
            transclude:true,
            replace:true,
            scope:false,
            priority:0,

            link:function(s,e,a){


            function watch(){
                if(e.attr("data-template")){
                    init(decodeURIComponent(e.attr("data-template")));
                    e.removeAttr("data-template");
                }
                else {
                    setTimeout(watch,10);
                }    
            }
            function init(html){
                var divRow=$("<div></div>");
                divRow.html(html);

                divRow=makeUpForm(divRow,a);
                $compile(divRow.contents())(s);
                
                divRow.contents().appendTo(e[0])

                s.$apply();
            }
            watch();
            }
        }
}]);
});