// 主页脚本
console.log('主页脚本加载成功!')
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

///////////////////////////////////////////////////////
// 注册组件
var Component_nav = {
    props: ['active_index'],
    template: '#template-index-nav',
    data: function () {
        return {
            nav_data: [{
                "name": "首页",
                "target": "/",
                "active": false,
            }, {
                "name": "登录",
                "target": "/login",
                "active": false,
            }, {
                "name": "注册",
                "target": "/join",
                "active": false,
            }],
        }
    },
    beforeMount: function () {
        // 加载组件：导航栏
        this.nav_data[this.active_index]['active'] = true;
    },
}
var Component_index = {
    template: '#template-index',
    components: {
        'index-nav': Component_nav,
    },
    beforeMount: function () {
        // 加载组件：首页
    },
}
var Component_login = {
    template: '#template-login',
    components: {
        'index-nav': Component_nav,
    },
    data: function () {
        return {
            username: '',
            password: '',
            input_check: false,
        }
    },
    watch: {
        username: function () {
            if (this.username.length > 3 && this.password.length > 3) {
                this.input_check = true;
            } else {
                this.input_check = false;
            }
        },
        password: function () {
            if (this.username.length > 3 && this.password.length > 3) {
                this.input_check = true;
            } else {
                this.input_check = false;
            }
        },

    },
    beforeMount: function () {
        // 加载组件：登录
    },
    methods: {
        login: function () {
            // 检查输入
            if (this.username.length > 3 && this.password.length > 3) {
                const data = {
                    "username": this.username,
                    "password": this.password
                };
                API.POST('/api/user.login', data, this.check);

            } else {

                alert('请输入正确的账号密码')
            }
        },
        check: function (resp) {
            if (resp.ok) {
                // 七天后过期
                var exdate=new Date()
                exdate.setDate(exdate.getDate()+7)
                // 操作cookies
                document.cookie = 'token=' + escape(resp.data.token) + ";expires=" + exdate.toGMTString();
                document.cookie = 'user_id=' + escape(resp.data.user_id) + ";expires=" + exdate.toGMTString();
                // 重定向到博客管理页
                location.assign('/b/'+resp.data.username+'/admin')
            } else {
                this.$snotify.error(resp.message, 'Error');
            }
        }
    },
}
var Component_join = {
    template: '#template-join',
    components: {
        'index-nav': Component_nav,
    },
    data: function () {
        return {
            username: '',
            password: '',
            input_check: false,
        }
    },
    watch: {
        username: function () {
            if (this.username.length > 3 && this.password.length > 3) {
                this.input_check = true;
            } else {
                this.input_check = false;
            }
        },
        password: function () {
            if (this.username.length > 3 && this.password.length > 3) {
                this.input_check = true;
            } else {
                this.input_check = false;
            }
        }
    },
    beforeMount: function () {
        // 加载组件：注册
    },
    methods: {
        join: function () {
            // 检查输入
            if (this.username.length > 3 && this.password.length > 3) {
                var data = {
                    "username": this.username,
                    "password": this.password
                };
                API.POST('/api/user.new', data, this.check);
            }
        },
        check:function(resp) {
            if (resp.ok) {
                // 推送消息
                this.$snotify.success('现在你可以尝试登录了！', '注册成功');
                // 重定向到登录
                this.$router.push('/login');
            } else {
                this.$snotify.error(resp.message, 'Error');
            }
        }
    }
}
///////////////////////////////////////////////////////

///////////////////////////////////////////////////////
// 路由
var router = new VueRouter({
    routes: [{
            path: '/',
            component: Component_index,
        },
        {
            path: '/login',
            component: Component_login,
        },
        {
            path: '/join',
            component: Component_join,
        },
    ]
})
///////////////////////////////////////////////////////

///////////////////////////////////////////////////////
// 主实例
var app = new Vue({
    el: '#app',
    router: router,
});
///////////////////////////////////////////////////////