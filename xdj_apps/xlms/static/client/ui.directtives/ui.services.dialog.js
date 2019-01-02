angularDefine(function(mdl){
    mdl.service("$dialog",["$compile",function($compile){
        function getScope(id) {
            var elem;
            $('.ng-scope').each(function(){
                var s = angular.element(this).scope(),
                    sid = s.$id;
    
                if(sid == id) {
                    elem = this;
                    return false; // stop looking at the rest
                }
            });
            return elem;
        }
        return function(scope){
            scope.$root.$compile=$compile
            scope.$root.$dialog=function(id){
                if(!id){
                    return $dialog(scope.$root)
                }
                else {
                    var ele=getScope(id)
                    subScope=angular.element(ele).scope()
                    return dialog(subScope)
                }
    
            }
        }
    }])
  
})