/*--how to use:
    <div b-select source="<dropdown datasource>" field-text="<Dispaly Field>" field-value="return value field when user select"  on-change=.. ng-model=../>
*/

angularDefine(function (mdl) {
    mdl.directive("bSelect", ["$parse", function ($parse) {
            return {
                restrict: "CEA",
                template:function(){
                    return "<select class=\"input-sm form-control\"></select>"
                },
                scope: false,
                replace: true,
                link: function (scope, ele, attr) {
                    debugger;
                    function applyData(data) {
                        ele.find("select").empty();
                        if (angular.isArray(data)) {
                            for (var i = 0; i < data.length; i++) {
                                var option = $("<option></option>");
                                option.html(data[i][attr["fieldText"]]);
                                option.attr("value", data[i][attr["fieldValue"]]);
                                option.appendTo(ele.find("select")[0]);
                            }
                        }
                    }
                    if (attr["source"]) {
                        var list = scope.$eval(attr["source"]);
                        applyData(list);
                        var val = scope.$eval(attr["ngModel"]);
                        ele.find("select").val(val);
                    }
                    var isChange = false;
                    scope.$watch(attr["ngModel"], function (value) {
                        if (isChange)
                            return;
                        ele.find("select").val(value);
                    });
                    scope.$watch(attr["source"], function (value, oldValue) {
                        if (value == oldValue)
                            return;
                        applyData(value);
                        var val = scope.$eval(attr["ngModel"]);
                        isChange = true;
                        ele.find("select").val(val);
                        isChange = false;
                    });
                    ele.find("select").bind("change", function () {
                        isChange = true;
                        if (attr["ngModel"]) {
                            $parse(attr["ngModel"]).assign(scope, $(this).val());
                        }
                        if (attr["ngChange"]) {
                            scope.$eval(attr['ngChange']);
                        }
                        scope.$applyAsync();
                        isChange = false;
                    });
                }
            };
        }]);
});
