/*--how to use:
    <div b-pager page-size=.. total-items=.. page-index=.. on-change=.. ng-model=../>
*/
angularDefine(function (mdl) {
    mdl.directive("bPager", ["$parse", function ($parse) {
            return {
                restrict: "CEA",
                replace: true,
                template:"<div></div>",
                link: function (scope, ele, attr) {
                    var cmp = {
                        pageSize: scope.$eval(attr["pageSize"]),
                        totalItems: scope.$eval(attr["totalItems"]),
                        pageIndex: scope.$eval(attr["pageIndex"]),
                        labelFirst: scope.$eval(attr["labelFirst"]),
                        labelLast: scope.$eval(attr["labelLast"]),
                        onChange: attr["onChange"],
                        hasPainted: undefined,
                        $pager: undefined
                    };
                    var isInorge = false;
                    function paint() {
                        if (cmp.$pager) {
                            cmp.$pager.twbsPagination('destroy');
                        }
                        ;
                        if (angular.isUndefined(cmp.pageIndex))
                            return;
                        if (angular.isUndefined(cmp.totalItems))
                            return;
                        if (angular.isUndefined(cmp.pageSize))
                            return;
                        var totalPages = cmp.totalItems / cmp.pageSize;
                        if (cmp.totalItems % cmp.pageSize > 0) {
                            totalPages++;
                        }
                        cmp.$pager = $(ele[0])["twbsPagination"]({
                            totalPages: totalPages,
                            visiblePages: 5,
                            startPage: cmp.pageIndex * 1 + 1,
                            prev: '<span aria-hidden="true">&laquo;</span>',
                            next: '<span aria-hidden="true">&raquo;</span>',
                            first: '<span aria-hidden="true">&#124;&laquo;</span>',
                            last: '<span aria-hidden="true">&raquo;&#124;</span>',
                            onPageClick: function (event, page) {
                                isInorge = true;
                                if (cmp.hasPainted) {
                                    if (cmp.onChange) {
                                        var fn = scope.$eval(cmp.onChange);
                                        if (angular.isFunction(fn)) {
                                            fn(page - 1);
                                        }
                                    }
                                }
                                cmp.hasPainted = true;
                                isInorge = false;
                            }
                        });
                    }
                    paint();
                    scope.$watch(attr["pageSize"], function (value) {
                        cmp.hasPainted = false;
                        cmp.pageSize = value;
                        paint();
                    });
                    scope.$watch(attr["totalItems"], function (value) {
                        cmp.hasPainted = false;
                        cmp.totalItems = value;
                        paint();
                    });
                    scope.$watch(attr["pageIndex"], function (value) {
                        if (isInorge)
                            return;
                        cmp.hasPainted = false;
                        cmp.pageIndex = value;
                        paint();
                    });
                }
            };
        }]);
});
