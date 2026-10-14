import { createRouter, createWebHistory } from "vue-router";
import { AUTH_DISABLED } from "../studio/config";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "Home",
      component: () => import("../studio/Home.vue"),
      meta: { standalone: true },
    },
    { path: "/home", redirect: "/" },
    {
      path: "/dashboard",
      name: "Dashboard",
      component: () => import("../studio/Dashboard.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/batch-process",
      name: "BatchProcess",
      component: () => import("../studio/Batch.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/annotation",
      name: "Annotation",
      component: () => import("../studio/Annotation.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/medllm",
      name: "MedLLM",
      component: () => import("../studio/Consultation.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/corrector",
      name: "Corrector",
      component: () => import("../views/Corrector.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      component: () => import("../views/Login.vue"),
      meta: { authPage: true },
    },
    {
      path: "/register",
      component: () => import("../views/Register.vue"),
      meta: { authPage: true },
    },
    {
      path: "/auth",
      component: () => import("../views/Auth.vue"),
      meta: { authPage: true },
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
  scrollBehavior: () => ({ top: 0 }),
});
router.beforeEach((to) => {
  if (AUTH_DISABLED) return to.meta.authPage ? "/dashboard" : true;
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) return "/auth";
  if (to.meta.authPage && token) return "/dashboard";
  return true;
});
export default router;
