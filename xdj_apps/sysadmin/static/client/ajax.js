
function ajax(){
    if(!window.____ajax){
        window.____ajax =new function(){
            var ax=this;
            
            ax.onBeforePost=function(callback){
                ax._onBeforePost=callback;
                return ax;
            }
            ax.onAfterPost=function(callback){
                ax._onAferPost=callback;
                return ax;
            }
            ax.onError=function(callback){
                ax._onError=callback;
                return ax;
            }
            ax.create=function(url){
                function retCreate(url){
                    var owner=this;
                    owner.url=url;
                    owner.call=function(id){
                        function retCall(id){
                            var me=this;
                            me.owner=owner;
                            me.id=id;
                            me.data=function(_data){
                                me._data=_data;
                                return me;
                            }
                            me.error=function(callback){
                                me._error=callback;
                                return me;
                            }
                            me.done=function(callback){
                                var sender=undefined;
                                if(ax._onBeforePost){
                                    sender=ax._onBeforePost(me);
                                }
                                $.ajax({
                                    url:owner.url,
                                    method:"POST",
                                    headers:{"AJAX-POST":me.id},
                                    data:JSON.stringify(me._data),
                                    contentType: "application/json; charset=utf-8",
                                    dataType: "json",
                                    success:function(res){
                                        if(ax._onAferPost){
                                            ax._onAferPost(me,sender);
                                        }
                                        if(callback){
                                            callback(res);
                                        }
                                    },
                                    error:function(ex){
                                        if(ax._onAferPost){
                                            ax._onAferPost(me,sender);
                                        }
                                        
                                        var continueRaiseError=false;
                                        if(me._error){
                                            continueRaiseError=me._error(ex.responseText);
                                            if(continueRaiseError){
                                                if(ax._onError){
                                                    ax._onError(me,ex);
                                                }
                                            }
                                        }
                                        else {
                                            if(ax._onError){
                                                ax._onError(me,ex);
                                            }
                                        }
                                    }
            
                                });
                            }
                        }
                        return new retCall(id);
                    }
                }
                return new retCreate(url);
            }
            if(!ajax.create){
                ajax.create=ax.create;
            }
        }
    }
    return window.____ajax;
}

