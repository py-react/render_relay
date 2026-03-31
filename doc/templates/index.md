<script setup>
import { data as templates } from './templates.data'
import TemplateCard from '../.vitepress/theme/components/TemplateCard.vue'
</script>

# Project Templates

Get a head start on your next Brahma project with these pre-configured, high-performance templates.

<div class="template-grid">
  <TemplateCard 
    v-for="template in templates" 
    :key="template.id" 
    :template="template" 
  />
</div>

<style>
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}
</style>
