// 主题：base 
// 作用于：用户主页
console.log('管理页面脚本加载成功!')
///////////////////////////////////////////////////////
// API
var API = {
    "GET": function (url, fn) {
        fetch(url)
            .then(res => res.json())
            .then(res => {
                fn.call(this, res)
            })
            .catch(res => {
                fn.call(this, res)
            })
    },
    "POST": function (url, data, fn) {
        fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
            .then(res => res.json())
            .then(res => {
                fn.call(this, res)
            })
            .catch(res => {
                fn.call(this, res)
            })
    }
}
///////////////////////////////////////////////////////
function timetrans(date) {
    var date = new Date(date);
    var Y = date.getFullYear() + '-';
    var M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
    var D = (date.getDate() < 10 ? '0' + (date.getDate()) : date.getDate()) + ' ';
    var h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
    var m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':';
    var s = (date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds());
    return Y + M + D + h + m + s;
}
///////////////////////////////////////////////////////
// 注册组件
var Component_nav = {
    props: ['active_index'],
    template: '#template-index-nav',
    data: function () {
        return {
            nav_data: [{
                "name": CONFIG['blog_name'],
                "target": "/",
                "active": false,
            }, ],
            icon_url: CONFIG['icon_url'],
        }
    },
    beforeMount: function () {
        console.log('加载组件：导航栏');
    },
}

var Component_index = {
    template: '#template-index',
    components: {
        'index-nav': Component_nav,
    },
    data: function () {
        return {
            blog_info: CONFIG,
            articles: '',
        }
    },
    beforeMount: function () {
        console.log('加载组件：用户首页');
        API.GET('/api/articles/' + this.blog_info.user_id, this.check)
    },
    methods: {
        check: function (resp) {
            // 如果请求数据成功，则保存到List_data变量中
            if (resp.ok) {
                this.articles = resp.data;
            }
        },
        timetrans:function(date){
            return timetrans(date)
        }
    }
}

var Component_article = {
    props: ['id'],
    template: '#template-article',
    components: {
        'index-nav': Component_nav,
    },
    data: function () {
        return {
            blog_info: CONFIG,
            article: '',
        }
    },
    beforeMount: function () {
        console.log('加载组件：用户首页');
        API.GET('/api/article.one/' + this.id, this.check)
    },
    methods: {
        check: function (resp) {
            // 如果请求数据成功，则保存到List_data变量中
            if (resp.ok) {
                this.article = resp.data;
            }
        },
        timetrans:function(date){
            return timetrans(date)
        }
    }
}
///////////////////////////////////////////////////////
// 路由
var router = new VueRouter({
    routes: [{
            path: '/',
            component: Component_index,
        },
        {
            path: '/article/:id',
            component: Component_article,
            props: true
        },

    ]
})


///////////////////////////////////////////////////////
// 主实例
var app = new Vue({
    el: '#app',
    router: router,
    data: {}
});