import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const blogDir = path.join(__dirname, '../src/content/blog');

function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')        // Replace spaces with -
        .replace(/[^\w\-]+/g, '')    // Remove all non-word chars
        .replace(/\-\-+/g, '-')      // Replace multiple - with single -
        .replace(/^-+/, '')          // Trim - from start of text
        .replace(/-+$/, '');         // Trim - from end of text
}

async function renameFiles() {
    try {
        const files = fs.readdirSync(blogDir).filter(file => file.endsWith('.md') && file !== 'welcome.md');

        console.log(`Found ${files.length} article files to process.`);

        for (const file of files) {
            const oldPath = path.join(blogDir, file);
            let content = fs.readFileSync(oldPath, 'utf8');

            // Regex to find "**Title:** Some Title" or "**Title:**: Some Title"
            // It searches in the whole file, but typically it's near the top.
            const titleBodyMatch = content.match(/\*\*Title:?\*\*\s*(.+)/i);

            if (titleBodyMatch && titleBodyMatch[1]) {
                const realTitle = titleBodyMatch[1].trim();

                // Update Frontmatter
                // Replace title: 'Old Title' with title: 'Real Title'
                content = content.replace(/^title:\s*['"].*?['"]$/m, `title: '${realTitle.replace(/'/g, "\\'")}'`);

                // Generate new slug
                const newSlug = slugify(realTitle);
                const newFilename = `${newSlug}.md`;
                const newPath = path.join(blogDir, newFilename);

                // Save content with new title
                fs.writeFileSync(oldPath, content);

                // Rename file
                if (oldPath !== newPath) {
                    fs.renameSync(oldPath, newPath);
                    console.log(`Updated and Renamed: ${file} -> ${newFilename} ("${realTitle}")`);
                } else {
                    console.log(`Updated Content Only: ${file} (Name already matched)`);
                }
            } else {
                console.warn(`Could not find "**Title:**" pattern in ${file}`);
            }
        }
    } catch (error) {
        console.error('Error renaming files:', error);
    }
}

renameFiles();
