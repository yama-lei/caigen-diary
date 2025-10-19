<template>
  <div class="min-h-screen paper-bg">
    <!-- Header -->
    <header class="bg-nju-purple text-white shadow-lg sticky top-0 z-50">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <h1 class="text-2xl font-bold font-serif"> 菜根日记存档</h1>
            <p class="text-sm text-nju-light font-sans hidden md:block">菜根日记是杜厦图书馆二楼大厅入门处，学生自发组织的留言板</p>
          </div>
          <nav class="flex space-x-4 font-sans">
            <router-link to="/" class="hover:text-nju-light transition-colors px-3 py-2 rounded" active-class="bg-nju-dark">
              首页
            </router-link>
            <router-link to="/search" class="hover:text-nju-light transition-colors px-3 py-2 rounded" active-class="bg-nju-dark">
              搜索与筛选
            </router-link>
            <router-link to="/stats" class="hover:text-nju-light transition-colors px-3 py-2 rounded" active-class="bg-nju-dark">
              统计
            </router-link>
            <router-link to="/about" class="hover:text-nju-light transition-colors px-3 py-2 rounded" active-class="bg-nju-dark">
              关于
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-library-wood text-white mt-16 py-8">
      <div class="container mx-auto px-4 text-center">
        <p class="text-xs text-library-paper/50 mt-4 font-sans">
          © 2025 菜根日记存档
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// No additional script needed for now
</script>

<style scoped>
header {
  backdrop-filter: blur(10px);
}
</style>

