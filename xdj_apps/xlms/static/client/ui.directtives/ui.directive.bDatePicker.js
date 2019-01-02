/*
    how to use:
        <div b-date-picker></div>
        default format was set in $root.defaultDateFormat
*/
angularDefine(function (mdl) {
    mdl.directive('bDatePicker', ["$parse", function ($parse) {

        return {
        restrict: "CEA",
        replace: true,
        template: function(){
            if(mdl.isSmallSize){
                return "<div class='input-group-sm input-group'><input type='text' class='form-control'/><span class=\"input-group-sm  input-group-addon\"><span class=\"glyphicon glyphicon-calendar\"></span></div>";
            }
            else {
                    return "<div class='input-group'><input type='text' class='form-control'/><span class=\"input-group-addon\"><span class=\"glyphicon glyphicon-calendar\"></span></div>";
            }
        },
        link: function (scope, ele, attr) {
            var format = scope.$root.defaultDateFormat||'dd/mm/yyyy';
            if (attr.format) {
                format = scope.$eval(attr.format);
            }
            $(ele[0]).find("input").datepicker({
                language: "vi",
                format: format, allowEmpty: true, clearBtn: true, keepEmptyValues:true
            });

            var isAutoChange = false;
            if (attr.ngModel) {
                var val = scope.$eval(attr.ngModel);
                if ((!val) || (val == null)) {
                    $(ele[0]).find("input").datepicker("update", null);
                    ////$(ele[0]).find("input").datepicker().data('datepicker').format(formar);

                }

                else {
                    if (typeof val === "string") {
                        try {
                            changeByModel = true;

                            //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                            $(ele[0]).find("input").datepicker("update", new Date(val));
                            changeByModel = false;
                        }
                        catch (ex) {
                            changeByModel = true;
                            $(ele[0]).find("input").datepicker("update", null);
                            //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                            changeByModel = false;
                        }
                    }
                    else {
                        changeByModel = true;

                        //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                        $(ele[0]).find("input").datepicker("update", val);
                        changeByModel = false;
                    }
                }
            }
            var changeByModel = false;
            var transform = false;
            scope.$watch(attr.ngModel, function (val, oldVal) {
                if (val === "") {
                    changeByModel = true;
                    $(ele[0]).find("input").datepicker("update", "");
                    //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                    changeByModel = false;
                    return;
                }
                if (transform) return;
                if (isAutoChange) return;
                if ((!val) || (val == null)) {
                    changeByModel = true;
                    $(ele[0]).find("input").datepicker("update", null);
                    //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                    changeByModel = false;
                }
                else {
                    if (typeof val === "string") {
                        try {
                            changeByModel = true;

                            //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                            $(ele[0]).find("input").datepicker("update", new Date(val));
                            transform = true;
                            $parse(attr.ngModel).assign(scope, new Date(val));
                            transform = false;
                            changeByModel = false;
                        }
                        catch (ex) {
                            changeByModel = true;
                            $(ele[0]).find("input").datepicker("update", null);
                            //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                            changeByModel = false;
                        }
                    }
                    else {
                        changeByModel = true;

                        //$(ele[0]).find("input").datepicker().data('datepicker').format(formar);
                        $(ele[0]).find("input").datepicker("update", val);
                        changeByModel = false;
                    }
                }
            });
            $(ele[0]).find("input").on("change", function () {
                if (changeByModel) return;
                var val = $(ele[0]).find("input").datepicker('getDate');
                if ($(ele[0]).find("input").val() === "") {
                    isAutoChange = true;
                    $parse(attr.ngModel).assign(scope, null);
                    isAutoChange = false;
                    return;
                }
                if ((val && (val.toString() === "Invalid Date")) || (!val)) {
                    isAutoChange = true;
                    $parse(attr.ngModel).assign(scope, null);
                    isAutoChange = false;
                    return;
                }
                isAutoChange = true;
                $parse(attr.ngModel).assign(scope, val);
                isAutoChange = false;

            })
        }
    }

}])})