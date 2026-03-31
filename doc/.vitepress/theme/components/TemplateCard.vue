<script setup lang="ts">
defineProps<{
  template: {
    title: string
    description: string
    thumbnail: string
    repo: string
  }
}>()
</script>

<template>
  <div class="template-card">
    <div class="thumbnail-wrapper">
      <img :src="template.thumbnail" :alt="template.title" />
    </div>
    <div class="content">
      <h3>{{ template.title }}</h3>
      <p>{{ template.description }}</p>
      <div class="actions">
        <a :href="template.repo" target="_blank" class="repo-link">View Repo</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.template-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
}

.template-card:hover {
  transform: translateY(-8px);
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 12px 24px -10px rgba(255, 153, 51, 0.2);
}

.thumbnail-wrapper {
  aspect-ratio: 16 / 9;
  background: var(--vp-c-bg-mute);
  overflow: hidden;
}

.thumbnail-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.template-card:hover .thumbnail-wrapper img {
  transform: scale(1.05);
}

.content {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.content p {
  font-size: 0.95rem;
  line-height: 1.6;
  opacity: 0.8;
  margin-bottom: 1.5rem;
}

.actions {
  margin-top: auto;
}

.repo-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: var(--vp-c-brand-1);
  color: white !important;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none !important;
  transition: opacity 0.2s;
}

.repo-link:hover {
  opacity: 0.9;
}
</style>
