import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import MedLLM from '../views/MedLLM.vue';
import Corrector from '../views/Corrector.vue';
import BatchProcess from '../pages/BatchProcess.vue';
import Annotation from "../pages/Annotation.vue";
import Auth from "../views/Auth.vue"
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/medllm',
    name: 'MedLLM',
    component: MedLLM,
    meta: { requiresAuth: true }
  },
  {
    path: '/corrector',
    name: 'Corrector',
    component: Corrector,
    meta: { requiresAuth: true }
  },
  {
    path: '/batch-process',
    name: 'BatchProcess',
    component: BatchProcess,
    meta: { requiresAuth: true }
  },
  {
    path: '/annotation',
    name: 'Annotation',
    component: Annotation,
    meta: { requiresAuth: true }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: Auth,

  },
  {
    path: '/',
    redirect: '/auth'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  
  if (to.meta.requiresAuth && !token) {
    next('/auth');
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/');
  } else {
    next();
  }
});

export default router;