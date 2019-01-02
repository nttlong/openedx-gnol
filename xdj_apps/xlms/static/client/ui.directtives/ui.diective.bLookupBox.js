angularDefine(function(mdl){
    mdl.directive("bLookupBox", ["$parse", function ($parse) {
        return {
            restrict: "CEA",
            replace: true,
            template:"<div class=\"input-group input-group-sm\">"+
                     "<input type=\"text\" class=\"form-control\">"+
                     "<span class=\"input-group-addon\" id=\"basic-addon2\">..</span>"+
                     "</div>",
            link: function (scope, ele, attr) {

            }
        };
    }]);
});