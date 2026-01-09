import fs from 'fs';
import path from 'path';
import mammoth from 'mammoth';
import TurndownService from 'turndown';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const turndownService = new TurndownService();

const inputDir = path.join(__dirname, '../public/downloads');
const outputDir = path.join(__dirname, '../src/content/blog');

async function processFiles() {
    try {
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const files = fs.readdirSync(inputDir).filter(file => file.endsWith('.docx'));

        console.log(`Found ${files.length} docx files.`);

        for (const file of files) {
            const filePath = path.join(inputDir, file);
            const result = await mammoth.convertToHtml({ path: filePath });
            const html = result.value;
            const markdown = turndownService.turndown(html);

            // Infer title from filename
            const title = file.replace('.docx', '').replace('Artigo #', 'Article ').trim();
            const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

            // Extract first paragraph as description if possible, or use default
            const descriptionMatch = markdown.split('\n\n')[0];
            const description = descriptionMatch ? descriptionMatch.substring(0, 150).replace(/"/g, '\\"') + '...' : 'Interesting financial insights powered by AI.';

            const frontmatter = `---
title: '${title}'
description: "${description}"
pubDate: ${new Date().toISOString().split('T')[0]}
author: 'SmartAI Team'
image: '/images/blog-placeholder.jpg'
---
`;

            const finalContent = `${frontmatter}\n${markdown}`;
            const outputPath = path.join(outputDir, `${slug}.md`);

            fs.writeFileSync(outputPath, finalContent);
            console.log(`Converted: ${file} -> ${slug}.md`);
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

processFiles();
