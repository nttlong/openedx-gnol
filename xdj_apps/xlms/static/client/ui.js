!function(e,n){"object"==typeof exports&&"undefined"!=typeof module?n():"function"==typeof define&&define.amd?define(n):n()}(0,function(){"use strict";function e(e){var n=this.constructor;return this.then(function(t){return n.resolve(e()).then(function(){return t})},function(t){return n.resolve(e()).then(function(){return n.reject(t)})})}function n(){}function t(e){if(!(this instanceof t))throw new TypeError("Promises must be constructed via new");if("function"!=typeof e)throw new TypeError("not a function");this._state=0,this._handled=!1,this._value=undefined,this._deferreds=[],u(e,this)}function o(e,n){for(;3===e._state;)e=e._value;0!==e._state?(e._handled=!0,t._immediateFn(function(){var t=1===e._state?n.onFulfilled:n.onRejected;if(null!==t){var o;try{o=t(e._value)}catch(f){return void i(n.promise,f)}r(n.promise,o)}else(1===e._state?r:i)(n.promise,e._value)})):e._deferreds.push(n)}function r(e,n){try{if(n===e)throw new TypeError("A promise cannot be resolved with itself.");if(n&&("object"==typeof n||"function"==typeof n)){var o=n.then;if(n instanceof t)return e._state=3,e._value=n,void f(e);if("function"==typeof o)return void u(function(e,n){return function(){e.apply(n,arguments)}}(o,n),e)}e._state=1,e._value=n,f(e)}catch(r){i(e,r)}}function i(e,n){e._state=2,e._value=n,f(e)}function f(e){2===e._state&&0===e._deferreds.length&&t._immediateFn(function(){e._handled||t._unhandledRejectionFn(e._value)});for(var n=0,r=e._deferreds.length;r>n;n++)o(e,e._deferreds[n]);e._deferreds=null}function u(e,n){var t=!1;try{e(function(e){t||(t=!0,r(n,e))},function(e){t||(t=!0,i(n,e))})}catch(o){if(t)return;t=!0,i(n,o)}}var c=setTimeout;t.prototype["catch"]=function(e){return this.then(null,e)},t.prototype.then=function(e,t){var r=new this.constructor(n);return o(this,new function(e,n,t){this.onFulfilled="function"==typeof e?e:null,this.onRejected="function"==typeof n?n:null,this.promise=t}(e,t,r)),r},t.prototype["finally"]=e,t.all=function(e){return new t(function(n,t){function o(e,f){try{if(f&&("object"==typeof f||"function"==typeof f)){var u=f.then;if("function"==typeof u)return void u.call(f,function(n){o(e,n)},t)}r[e]=f,0==--i&&n(r)}catch(c){t(c)}}if(!e||"undefined"==typeof e.length)throw new TypeError("Promise.all accepts an array");var r=Array.prototype.slice.call(e);if(0===r.length)return n([]);for(var i=r.length,f=0;r.length>f;f++)o(f,r[f])})},t.resolve=function(e){return e&&"object"==typeof e&&e.constructor===t?e:new t(function(n){n(e)})},t.reject=function(e){return new t(function(n,t){t(e)})},t.race=function(e){return new t(function(n,t){for(var o=0,r=e.length;r>o;o++)e[o].then(n,t)})},t._immediateFn="function"==typeof setImmediate&&function(e){setImmediate(e)}||function(e){c(e,0)},t._unhandledRejectionFn=function(e){void 0!==console&&console&&console.warn("Possible Unhandled Promise Rejection:",e)};var l=function(){if("undefined"!=typeof self)return self;if("undefined"!=typeof window)return window;if("undefined"!=typeof global)return global;throw Error("unable to locate global object")}();"Promise"in l?l.Promise.prototype["finally"]||(l.Promise.prototype["finally"]=e):l.Promise=t});
window.___bootstrapUI___= angular.module("q-ui", []);
window.loadCSS = function(href) {

    var cssLink = $("<link>");
    $("head").append(cssLink); //IE hack: append before setting href
  
    cssLink.attr({
      rel:  "stylesheet",
      type: "text/css",
      href: href
    });
  
  };
var _dialog_root_url;
var ___uiReady__=undefined;
function uiReady(callback){
    ___uiReady__=callback;
}
var ___rootDir__=undefined;
function loadScripts(paths){
    var src=$($("script")[$("script").length-1]).attr("src");
    var items=src.split('/');

    var relPath=src.substring(0,src.length-items[items.length-1].length);
    ___rootDir__=relPath;
    angular.forEach(paths,function(path){
          $.getScript(relPath+path,
            function(data, textStatus, jqxhr ){
                console.log(relPath+path)
                
            }
          );
    })
   
}
function addCss(paths){
    angular.forEach(paths,function(path){
        var css=$("<link>");
        css.appendTo($("head")[0]);
        css.attr({
            rel:  "stylesheet",
            type: "text/css",
            href: ___rootDir__+path
      });
    });
}
function addScripts(paths,done){
    function runScript(index){
        if(index>=paths.length){
            if(done){
                done();
            }
            return;
        }
        else {
            $.getScript(___rootDir__+paths[index],
                function(data, textStatus, jqxhr ){
                    runScript(index+1);
                    console.log(___rootDir__+paths[index])
                }
              );
        }
    }
    runScript(0);
}


function angularDefine(callback){
    if(!window.___bootstrapUI___){
        window.___bootstrapUI___= angular.module("q-ui", []);
    }
    callback(window.___bootstrapUI___);
}
function dialog_root_url(value) {
    _dialog_root_url = value;
}
function findScopeById(id){
    var eles=$(".ng-scope");
    var ret=undefined;
    for(var i=0;i<eles.length;i++){
        ret=angular.element(eles[i]).scope();
        if(ret.$id===id){
            break;
        }
        else {
            ret=undefined;
        }
    }
    return ret;
}
function dialog($scope) {
    if(angular.isNumber($scope)){
        $scope=findScopeById($scope);
    }
    function getScript(content) {
        if (content.indexOf("<body>") > -1) {
            var x = content.indexOf("<body>") + "<body>".length;
            var y = content.indexOf("</body>");
            content = content.substring(x, y);
        }
        var ret = [];
        var i = content.indexOf("<script>");
        while (i > -1) {
            var j = content.indexOf("</script>", i);
            var script = content.substring(i + "<script>".length, j);
            ret.push(script);
            content = content.substring(0, i) + content.substring(j + "</script>".length, content.length);
            i = content.indexOf("<script>");
        }
        return {
            scripts: ret,
            content: content
        };
    }
    function compile(scope, scripts, content,_params) {
        var subScope = scope.$new(true, scope);

        for (var i = 0; i < scripts.length; i++) {
            var fn = eval(scripts[i]);
            fn(subScope,_params);
        }
        var frm = $('<div><div class="modal fade" id="myModal" role="dialog">' +
            '<div class="modal-dialog">' +
            '<div class="modal-content">' +

            '<div class="modal-header">' +


            '<h4 class="modal-title"><img src=""/ style="height:40px"><span>...</span></h4>' +
            '<button type="button" class="close" data-dismiss="modal">&times;</button>' +
            '</div>' +
            '<div class="modal-body">' +

            '</div>' +
            '</div></div>'
        );
        var $ele = $("<div>" + content + "</div>");

        var child = $($ele.children()[0])
        frm.attr("title",child.attr("title"))
        frm.attr("icon",child.attr("icon"))
        $ele.children().appendTo(frm.find(".modal-body")[0]);
        subScope.$element=frm

        subScope.$watch(function () {
            return subScope.$element.find(".modal-body").children().attr("title");
        }, function (val) {
            if(angular.isDefined(val)){
                subScope.$element.find(".modal-title span").html(val);
            }
        });
        subScope.$watch(function () {
            return subScope.$element.find(".modal-body").children().attr("icon");
        }, function (val) {
            if(angular.isDefined(val)){
                subScope.$element.find(".modal-title img").attr("src", val);
            }
            else{
                subScope.$element.find(".modal-title img").hide()
            }

        });
        if(!$scope.$root.$compile){
            throw("Please use '$compile' at controller then set '$scope.$root.$compile=$compile'")
        }
        $scope.$root.$compile(frm.contents())(subScope);
        subScope.$element = $(frm.children()[0]);
        subScope.$applyAsync();

        return subScope;
    }
    function ret(scope) {
        var me = this;
        me.url = function (_url) {
            if (_dialog_root_url) {
                me._url = _dialog_root_url + "/" + _url;
            }
            else {
                me._url = _url;
            }

            return me;
        }
        me.params=function(data){
            me._params=data;
            return me;
        }
        me.done = function (callback) {


            $.ajax({
                method: "GET",
                url: me._url,
                success: function (res) {
                    var ret = getScript(res);
                    var sScope = compile(scope, ret.scripts, ret.content,me._params);
                    if (callback) {
                        callback(sScope);
                    }
                    sScope.$element.appendTo("body");
                    function watch() {
                        if (!$.contains($("body")[0], sScope.$element[0])) {
                            sScope.$destroy();
                        }
                        else {
                            setTimeout(watch, 500);
                        }
                    }
                    watch();
                    sScope.$element.modal()
                        .on("hidden.bs.modal", function () {
                            sScope.$element.remove();

                        });

                    function watch() {
                        if (!$.contains($("body")[0], sScope.$element[0])) {

                            sScope.$destroy();
                        }
                        else {
                            setTimeout(watch, 500);
                        }
                    }
                    sScope.$doClose = function () {
                        sScope.$element.modal('hide')
                    }
                    watch();
                }
            })
        }
    }
    return new ret($scope);
}
function $url() {
    function ret() {
        var me = this;
        me.data = {};
        if (window.location.href.indexOf("#") > -1) {
            var ref = window.location.href.split('#')[1];
            var items = ref.split('&');
            for (var i = 0; i < items.length; i++) {
                me.data[items[i].split('=')[0]] = items[i].split('=')[1];
            }
        }
        me.param = function (key, value) {
            me.data[key] = value;
            return me;
        }
        me.clear = function () {
            me.data = {}
            return me;
        }
        me.url = function () {
            var ret = "";
            var keys = Object.keys(me.data);
            for (var i = 0; i < keys.length; i++) {
                ret += keys[i] + "=" + me.data[keys[i]] + "&"
            }
            return ret.substring(0, ret.length - 1);
        }
        me.apply = function () {
            window.location.href = "#" + decodeURIComponent( me.url());
        }

    }
    return new ret();
}
function history_navigator($scope) {
    var oldUrl;
    function historyMonitorStart(handler) {
        function run() {
            if (oldUrl != window.location.href) {

                if (historyChangeCallback.length > 0) {
                    if (window.location.href.indexOf('#') > -1) {
                        var data = {};
                        var url = window.location.href.split('#')[1];
                        var items = url.split('&');
                        var ret = {};
                        for (var i = 0; i < items.length; i++) {
                            data[items[i].split('=')[0]] = decodeURI(window["unescape"](items[i].split('=')[1]));
                        }
                        for (var i = 0; i < historyChangeCallback.length; i++) {
                            historyChangeCallback[i](data);
                        }
                        var keys = Object.keys($scope.$history.events);
                        for (var i = 0; i < keys.length; i++) {
                            if (!$scope.$history.events[keys[i]].hasStartCall) {
                                var obj = {
                                    key: keys[i],
                                    data: data,
                                    done: function () {
                                        if ($scope.$history.events[obj.key])
                                            $scope.$history.events[obj.key].handler(obj.data);
                                    }
                                }
                                setTimeout(function () {
                                    obj.done();
                                }, 300);

                            }
                        }

                    }
                    else {
                        historyChangeCallback[historyChangeCallback.length - 1]({});
                    }
                }
                oldUrl = window.location.href;
            }
            setTimeout(run, 100);
        }
        run();
    }

    var historyChangeCallback = [];
    function applyHistory(scope) {

        scope.$history = {
            isStart: true,
            events: {},
            data: function () {
                if (window.location.href.indexOf('#') == -1)
                    return {};
                var url = window.location.href.split('#')[1];
                var items = url.split('&');
                var ret = {};
                for (var i = 0; i < items.length; i++) {
                    ret[items[i].split('=')[0]] = decodeURI(window["unescape"](items[i].split('=')[1]));
                }
                return ret;
            },
            change: function (callback) {
                var _data = scope.$history.data();
                callback(_data);
                scope.$$$$historyCallback = callback;
                historyChangeCallback.push(callback);

            },
            redirectTo: function (bm) {
                window.location.href = bm;
            },
            onChange: function (subScope, handler) {

                scope.$history.events["scope_" + subScope.$id] = {
                    handler: handler,
                    hasStartCall: true,
                    scope: subScope
                };
                subScope.$on("$destroy", function () {
                    delete scope.$history.events["scope_" + subScope.$id];
                });
                if (scope.$history.events["scope_" + subScope.$id].hasStartCall) {
                    handler(scope.$history.data());
                    scope.$history.events["scope_" + subScope.$id].hasStartCall = false;
                }

            }
        };
        function URLObject(obj) {
            obj.$url = this;
            var me = this;
            me.data = obj.$history.data();
            me.clear = function () {
                me.data = {};
                return me;
            };
            me.item = function (key, value) {
                if (!me.data) {
                    me.data = {};
                }
                me.data[key] = value;
                return me;
            };
            me.done = function () {
                var keys = Object.keys(me.data);
                var retUrl = "";
                for (var i = 0; i < keys.length; i++) {
                    retUrl += keys[i] + "=" + window["escape"](encodeURI(me.data[keys[i]])) + "&";
                }
                retUrl = window.location.href.split('#')[0] + '#' + retUrl.substring(0, retUrl.length - 1);
                return retUrl;
            };
            var x = 1;
        }
        new URLObject(scope);
        historyMonitorStart(historyChangeCallback);
    }
    return new applyHistory($scope);
}

function ng_app(modulelName,controllerName,injection, fn,ngStartSymbol,ngEndSymbol) {
    injection.push("imageupload","q-ui");
    var app = angular.module(modulelName, injection, function ($interpolateProvider) {
        if(ngStartSymbol){
            $interpolateProvider.startSymbol(ngStartSymbol);
            $interpolateProvider.endSymbol(ngStartSymbol);
        }
        
    });
    var controller = app.controller(controllerName, ["$compile", "$scope", function ($compile, $scope) {
        $scope.$root.$compile = $compile;
        $scope.$root.$dialog =dialog;
        history_navigator($scope.$root);
        fn($scope);
        
          
        $scope.$applyAsync();
    }]);
}
var _appDirectiveSetRootUrl;
function appDirectiveSetRootUrl(url) {
    _appDirectiveSetRootUrl = url;
}
window.___bootstrapUI___ = angular.module("q-ui", []);




