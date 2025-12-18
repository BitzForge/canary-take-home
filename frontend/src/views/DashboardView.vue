<template>
  <div class="page">
    <h1>Dashboard</h1>
    <button @click="linkGithub">Link GitHub account</button>

    <section v-if="repos.length" class="repos">
      <h2>Select a repository</h2>
      <ul>
        <li v-for="repo in repos" :key="repo.id">
          <label>
            <input
              type="radio"
              name="repo"
              :value="repo.full_name"
              v-model="selectedFullName"
            />
            {{ repo.full_name }}
          </label>
        </li>
      </ul>
      <button :disabled="!selectedRepo" @click="saveSelection">Save Selection</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

interface Repo {
  id: number | string
  full_name: string
}

const repos = ref<Repo[]>([])
const selectedFullName = ref<string>('')
const selectedRepo = computed<Repo | undefined>(() =>
  repos.value.find((r: Repo) => r.full_name === selectedFullName.value)
)

const linkGithub = async () => {
  try {
    const resp = await axios.get('/api/github/authorize-url/')
    window.location.href = resp.data.authorize_url
  } catch (e) {
    console.error('Failed to get GitHub authorize URL', e)
  }
}

const loadRepos = async () => {
  try {
    const resp = await axios.get('/api/github/repos/')
    repos.value = resp.data.repositories || []
  } catch (e) {
    console.warn('Could not load repos (maybe GitHub not linked yet)', e)
  }
}

const saveSelection = async () => {
  if (!selectedRepo.value) return
  try {
    await axios.post('/api/github/select-repo/', {
      repo_id: selectedRepo.value.id,
      full_name: selectedRepo.value.full_name,
    })
    alert('Repository selection saved and webhook registered.')
  } catch (e) {
    console.error('Failed to save selection', e)
  }
}

onMounted(() => {
  // Check if we just came back from GitHub OAuth
  const params = new URLSearchParams(window.location.search)
  if (params.get('github_linked') === 'true') {
    // Clean up URL and load repos
    window.history.replaceState({}, '', '/dashboard')
  }
  if (params.get('error')) {
    console.error('GitHub linking error:', params.get('error'))
  }
  loadRepos()
})
</script>

<style scoped>
.page {
  max-width: 600px;
  margin: 2rem auto;
}
.repos ul {
  list-style: none;
  padding: 0;
}
.repos li {
  margin-bottom: 0.5rem;
}
button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
}
</style>
