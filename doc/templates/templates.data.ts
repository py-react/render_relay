import fs from 'fs'
import path from 'path'

interface Template {
    id: string
    title: string
    description: string
    thumbnail: string
    repo: string
}

declare const data: Template[]
export { data }

export default {
    watch: ['./**/metadata.json'],
    load() {
        const templatesDir = path.resolve(__dirname, '.')
        const folders = fs.readdirSync(templatesDir).filter(f =>
            fs.statSync(path.join(templatesDir, f)).isDirectory() && !f.startsWith('.')
        )

        const templates: Template[] = []

        for (const folder of folders) {
            const metaPath = path.join(templatesDir, folder, 'metadata.json')
            if (fs.existsSync(metaPath)) {
                const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'))
                templates.push({
                    id: folder,
                    ...meta
                })
            }
        }

        return templates
    }
}
