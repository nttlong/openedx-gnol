/*
    <select2 data-source="..." field-value=".." field-text=".."></select2>
*/
angularDefine(function(mdl){

    mdl.directive("select2",["$parse","$compile",function($parse,$compile){
        return {
            restrict:"ECA",
            transclude:true,
            template:"<div><select style=\"width:100%\"></select><div ng-transclude style='display:none'></div></div>",
            replace:true,
            link:function(s,e,a){
                debugger;
                var templateResult= undefined;
                var templateSelection = undefined;
                if (e.attr("data-template-result")){
                    templateResult =decodeURIComponent(e.attr("data-template-result"))
                    e.removeAttr("data-template-result")
                }
                if (e.attr("data-template-selection")){
                    templateSelection =decodeURIComponent(e.attr("data-template-selection"))
                    e.removeAttr("data-template-selection")
                }
                var config={
                    data:s.$eval(a.source)||[],
                    placeholder: a.placeholder,
                    allowClear: true
                }
                if(templateResult){
                    config.templateResult =function(item){
                        if(item._x){
                            if(!item._x.html){
                                $parse("p").assign(item._x.scope,item._x.dataItem);
                                var html = $compile($(templateResult).contents())(item._x.scope)
                                item._x.html= html
                                item._x.scope.$applyAsync();
                            }
                            return item._x.html
                        }

                    }
                }
                if(templateSelection){
                    config.templateSelection =function(item){
                         if(item._x){
                            if(!item._x.selectedHtml){
                                $parse("p").assign(item._x.scope,item._x.dataItem);
                                var html = $compile($(templateSelection).contents())(item._x.scope)
                                item._x.selectedHtml= html
                                item._x.scope.$applyAsync();
                            }
                            return item._x.selectedHtml
                        }
                    }
                }
                var isManulaChange=false;
                var isChangeByBinding =false
                var instance=$(e[0]).find("select").select2(config).data("select2");
                instance.$element.on("select2:select",function(evt){
                    if (isChangeByBinding) {return;}
                    isManulaChange=true;
                    if(a.ngModel){
                        $parse(a.ngModel).assign(s,$(evt.currentTarget).val());
                    }
                    if(a.ngChange){
                        var fn=s.$eval(a.ngChange);
                        if(angular.isFunction(fn)){
                            fn($(evt.currentTarget).val());
                        }
                    }
                    s.$applyAsync();
                    isManulaChange=false;
                })
                a.$observe("placeholder",function(v){
                    config.placeholder=v;
                    instance.$element.select2(config);
                });
                s.$watch(a.ngModel,function(v,o){
                    if(isManulaChange) return;
                    if(v!=o){
                        isChangeByBinding = true;
                        instance.trigger("change");
                        isChangeByBinding = false;
                        
                    }
                });
                s.$on("$destroy",function(){
                    instance.$element.select2('destroy')
                })
                s.$watch(a.source,function(v,o){
                    if(o!==v){
                        //$(e[0]).select2("destroy");
                            var lst =[]
                            for(var i=0;i<v.length;i++){
                                var item ={}

                                lst.push({
                                    id:v[i][a.fieldValue],
                                    text:v[i][a.fieldText],
                                    _x:{
                                        dataItem:v[i],
                                        scope:s.$new(true)
                                    }

                                })
                            }
                            config.data=lst;
                            instance.$element.select2(config);
                            //instance=$(e[0]).select2(config).data("select2");
                            //instance.setData(v);
                    }
                })
                
            }
        }
    }]);
})
angularDefine(function(mdl){
    mdl.directive("templateResult",[function(){
         return {
            restrict:"ECA",
                compile: function(element, attributes){
                    var originHtml=element.html();
                    element.empty();
                    return {
                        pre: function(s, e, a, c, t){
                        e.parent().parent().attr("data-template-result",encodeURIComponent(originHtml));
                            e.remove();

                        },
                        post: function(s, e, a, c, t){

                        }
                    }
             }
        }
    }])
})
angularDefine(function(mdl){
    mdl.directive("templateSelection",[function(){
         return {
            restrict:"ECA",
                compile: function(element, attributes){
                    var originHtml=element.html();
                    element.empty();
                    return {
                        pre: function(s, e, a, c, t){
                        e.parent().parent().attr("data-template-selection",encodeURIComponent(originHtml));
                            e.remove();

                        },
                        post: function(s, e, a, c, t){

                        }
                    }
             }
        }
    }])
})