// 主页脚本
// 主题：base 
// 作用于：用户管理页 
///////////////////////////////////////////////////////
// API
var API = {
    "GET": function (url, fn) {
        fetch(url )
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
    },
    getCookie: function (c_name) {
        if (document.cookie.length > 0) {
            c_start = document.cookie.indexOf(c_name + "=")
            if (c_start != -1) {
                c_start = c_start + c_name.length + 1
                c_end = document.cookie.indexOf(";", c_start)
                if (c_end == -1) c_end = document.cookie.length
                return unescape(document.cookie.substring(c_start, c_end))
            }
        }
        return ""
    }
}
///////////////////////////////////////////////////////

///////////////////////////////////////////////////////
// 注册组件
var Component_nav = {
    props: ['active_index'],
    template: '#template-nav',
    data: function () {
        return {
            nav_data: [{
                    "name": "配置",
                    "target": "/",
                    "active": false,
                },
                {
                    "name": "管理",
                    "target": "/manage",
                    "active": false,
                },
                {
                    "name": "写作",
                    "target": "/writing",
                    "active": false,
                },
            ],
            icon_url: CONFIG['icon_url'],
        }
    },
    beforeMount: function () {
        // 加载组件：导航栏
        this.nav_data[this.active_index]['active'] = true;
    },
}

var Component_setting = {
    template: '#template-setting',
    components: {
        'index-nav': Component_nav,
    },
    data: function () {
        return {
            user_detail: '',
            is_changging: false,
        }
    },
    beforeMount: function () {
        // 加载组件：管理
        API.GET('/api/user.detail', this.load_detail);
    },
    methods: {
        submit_changging: function () {
            // 提交博客信息变更
            API.POST('/api/user.config', JSON.stringify(this.user_detail), this.success);
            this.$snotify.success('满意吗？', '修改成功');
        },
        load_detail: function (resp) {
            if (resp.ok) {
                this.user_detail = resp.data;
            }
        },
        success: function (resp) {
            if (resp.ok) {
                // 刷新数据
                API.GET('/api/user.detail', function(){});
                this.is_changging = false;
            }
        }
    }
}
var Component_manage = {
    template: '#template-manage',
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
        // 加载文章列表
        this.request_aericles()
    },
    methods: {
        save_articles: function (resp) {
            // 如果请求数据成功，则保存到本地
            if (resp.ok) {
                this.articles = resp.data;
            }
        },
        to_delete: function (e) {
            var r = confirm("确定要删除吗？");
            if (r) {
                API.GET('/api/article.delete/' + e.target.getAttribute('article_id'), this.request_aericles)
            }
        },
        request_aericles: function () {
            API.GET('/api/articles/' + this.blog_info.user_id, this.save_articles)
        }
    }
}
var Component_editor = {
    props: ['article_id'],
    template: '#template-editor',
    data: function () {
        return {
            _id: '',
            title: '',
            author: '',
            brief: '',
            content: '',
            auth: false,
            editer: '',
            saving: false,
            is_update: false,
        }
    },
    mounted: function () {
        // 加载组件：编辑器
        var E = window.wangEditor;
        this.editor = new E('#editor-bar', '#editor');
        this.editor.create();
        if (this.article_id) {
            // 如果传入了文章 id 则取得数据后载入
            this.is_update = true;
            API.GET('/api/article.one/' + this.article_id, this.load_article);
            this.$snotify.success('正在为你加载文章数据', '不要心急');
        }
    },
    methods: {
        save: function () {
            this.saving = true;
            var article = {
                "token": CONFIG['token'],
                "title": this.title,
                "author": this.author,
                "brief": this.brief,
                "content": this.editor.txt.html(),
                "auth": this.auth,
            }
            API.POST('/api/article.new', JSON.stringify(article), this.success);
        },
        update: function () {
            this.saving = true;
            var article = {
                "_id": this._id,
                "token": CONFIG['token'],
                "title": this.title,
                "author": this.author,
                "brief": this.brief,
                "content": this.editor.txt.html(),
                "auth": this.auth,
            }
            API.POST('/api/article.update', JSON.stringify(article), this.success);
        },
        success: function (resp) {
            if (resp.ok) {
                this.saving = false;
                this.$snotify.success('已经为你加载好了文章列表', '保存成功');
                this.$router.push('/manage');
            }
        },
        load_article: function (resp) {
            if (resp.ok) {
                this._id = resp.data._id;
                this.title = resp.data.title;
                this.author = resp.data.author;
                this.brief = resp.data.brief;
                this.editor.txt.html(resp.data.content);
            }
        }
    }
}
var Component_writing = {
    props: ['id'],
    template: '#template-writing',
    components: {
        'index-nav': Component_nav,
        'cus-editor': Component_editor,
    },
}

///////////////////////////////////////////////////////
// 路由
var router = new VueRouter({
    routes: [{
            path: '/',
            component: Component_setting,
        },
        {
            path: '/manage',
            component: Component_manage,
        },
        {
            path: '/writing',
            component: Component_writing,
        },
        {
            path: '/writing/:id',
            component: Component_writing,
            props: true
        },

    ]
})


///////////////////////////////////////////////////////
// 主实例
var app = new Vue({
    el: '#app',
    router: router,
    beforeMount:function(){
        document.title = '管理 - ' + CONFIG.blog_name;
    }
});