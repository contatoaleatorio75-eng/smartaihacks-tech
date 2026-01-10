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
const publicImgDir = path.join(__dirname, '../public/images/blog');

// Ensure image directory exists
if (!fs.existsSync(publicImgDir)) {
    fs.mkdirSync(publicImgDir, { recursive: true });
}

function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]+/g, '')
        .replace(/\-\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
}

async function processFiles() {
    try {
        const files = fs.readdirSync(inputDir).filter(file => file.endsWith('.docx'));

        console.log(`Found ${files.length} docx files.`);

        for (const file of files) {
            const filePath = path.join(inputDir, file);
            let imageCounter = 0;
            let featuredImage = null; // Store the first image found

            const slugBase = file.replace('.docx', '').toLowerCase().replace(/[^a-z0-9]+/g, '-');

            const options = {
                convertImage: mammoth.images.imgElement(function (image) {
                    return image.read("base64").then(function (imageBuffer) {
                        imageCounter++;
                        const extension = image.contentType.split('/')[1] || 'png';
                        const imageName = `${slugBase}-${imageCounter}.${extension}`;
                        const imagePath = path.join(publicImgDir, imageName);
                        const publicPath = `/images/blog/${imageName}`;

                        // Save image to disk
                        fs.writeFileSync(imagePath, Buffer.from(imageBuffer, 'base64'));

                        if (!featuredImage) {
                            featuredImage = publicPath;
                        }

                        return {
                            src: publicPath,
                            alt: `Image for ${slugBase}`
                        };
                    });
                })
            };

            const result = await mammoth.convertToHtml({ path: filePath }, options);
            const html = result.value;
            const markdown = turndownService.turndown(html);

            // Extract title again to keep consistent, or try to respect the renamed files?
            // Since we renamed files, we should try to match the content again or just re-generate best effort.
            // Let's rely on the internal title extraction again for consistency.
            const titleMatch = markdown.match(/\*\*Title:?\*\*\s*(.+)/i); // Simplified regex for speed
            let title = file.replace('.docx', '');
            if (titleMatch && titleMatch[1]) {
                title = titleMatch[1].trim();
            }
            const slug = slugify(title);

            // Extract first paragraph as description
            const descriptionMatch = markdown.split('\n\n').find(p => p.length > 50 && !p.startsWith('**'));
            const description = descriptionMatch ? descriptionMatch.substring(0, 150).replace(/"/g, '\\"') + '...' : 'Interesting financial insights powered by AI.';

            const frontmatter = `---
title: '${title.replace(/'/g, "\\'")}'
description: "${description}"
pubDate: ${new Date().toISOString().split('T')[0]}
author: 'SmartAI Team'
image: '${featuredImage || "/images/blog-placeholder.jpg"}'
---
`;

            const finalContent = `${frontmatter}\n${markdown}`;
            const outputPath = path.join(outputDir, `${slug}.md`);

            fs.writeFileSync(outputPath, finalContent);
            console.log(`Re-converted: ${file} -> ${slug}.md (First Image: ${featuredImage || 'None'})`);
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

processFiles();
