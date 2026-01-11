import { getCollection } from 'astro:content';

export async function GET() {
    const posts = await getCollection('blog');
    const index = posts.map(post => ({
        title: post.data.title,
        description: post.data.description,
        slug: post.slug,
        image: post.data.image || '/images/logo.png'
    }));

    return new Response(JSON.stringify(index), {
        status: 200,
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
