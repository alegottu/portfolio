from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import sys
import random
import os

template_env = Environment(loader=FileSystemLoader(searchpath='./'))
template = template_env.get_template('blog/postlayout.html')

# parse markdown files for posts
posts = dict()

for file in Path('blog/markdown').iterdir():
    md = Markdown(extensions=['meta', 'fenced_code'])
    post = md.convert(file.read_text())
    posts[post] = md.Meta

def date(text) -> int:
    nums = text.split('/')
    nums = list(map(int, nums))
    nums[0] *= 31
    nums[2] *= 365
    
    return sum(nums)

# sort posts by date
posts = dict(sorted(posts.items(), key=lambda item: -date(item[1]['date'][0])))

# render each post to its own html file
for post, config in posts.items():
    if config['category'][0] == 'WIP':
        continue

    with open(f"blog/posts/{config['file'][0]}.html", 'w') as output:
        image = config['image'][0]
        image = f"../images/{image}" if not "http" in image else image
        output.write(
            template.render(
                title=config['title'][0],
                banner=image,
                date=config['date'][0],
                excerpt=config.get('excerpt', [''])[0],
                post=post
            )
        )

# render the list of posts to the blog index (categorized)
template = template_env.get_template('blog/bloglayout.html')
listitems = ["","",""] # Español, Personal, Game Development

for post, config in posts.items():
    category = config['category'][0]
    file = f"posts/{config['file'][0]}.html"
    link = config['image'][0]
    link = f"images/{link}" if not "http" in link else link
    item = f"""\
<div class="col-4">
    <a href="{file}" class="image fit"><img src="{link}" alt="" /></a>
</div>
<div class="col-8">
    <a href="{file}"><h4>{config['title'][0]}</h4></a>
    <a href="{file}"><p>{config['date'][0]}</p></a>
</div>\n"""

    if category == "WIP":
        continue
    elif category == "Game Development":
        listitems[2] += item
    elif category == "Personal":
        listitems[1] += item
    else: # ID'd by language tag
        listitems[0] += item

with open("blog/blog.html", 'w') as output:
    output.write(
        template.render(
            items0=listitems[0],
            items1=listitems[1],
            items2=listitems[2],
        )
    )

# render index 
template = template_env.get_template('indexlayout.html')
images = ""

# generate gallery html
files = Path("images/").iterdir()
files = sorted(files, key=os.path.getmtime, reverse=True) if len(sys.argv) == 1 \
    else sorted(files, key=lambda x: random.random()) # NOTE: randomize gallery if any arg provided
for image in files:
    images += f'<div class="col-4"><img src="images/{image.name}" alt="" width="100%" /></div>'

# generate project carousel for index
projs = dict()
carousel = ""

for file in Path('projects/markdown').iterdir():
    md = Markdown(extensions=['meta'])
    temp = md.convert(file.read_text())
    projs[temp] = md.Meta
    # any pages without entries being duped over for now (key is by text in md)

# can probably reverse the sort instead of negative here
def score(score_str):
    return -int(score_str.strip('"'))

projs = dict(sorted(projs.items(), key=lambda item: score(item[1]['score'][0])))

for proj, config in projs.items():
    name = config['name'][0]
    ref = f"projects/posts/{name}.html"
    carousel += f"""\
    <article>
        <a href="{ref}" class="image featured"><img src="projects/images/{config['image'][0]}" alt="" /></a>
        <header>
            <h3><a href="{ref}">{name}</a></h3>
        </header>
        <p>{config['summary'][0]}</p>
    </article>"""

# NOTE: can have drop down menu for projects (list within list in nav for html)

# generate blog features
features = ""
posts = dict(sorted(posts.items(), key=lambda item: -date(item[1]['date'][0])))
num_posts = 0
max_posts = 3

for post, config in posts.items():
    if config['category'][0] != "WIP" and not 'feature' in config: # feature would = false meaning don't feature
        ref = f"blog/posts/{config['file'][0]}.html"
        img_link = config['image'][0]
        img_link = f"blog/images/{img_link}" if not "http" in img_link else img_link
        features += f"""\
        <article class="col-4 col-12-mobile special">
            <a href="{ref}" class="image featured"><img src="{img_link}" alt="" /></a>
            <header>
                <h3><a href="{ref}">{config['title'][0]}</a></h3>
            </header>
            <p>{config['summary'][0]}</p>
        </article>"""
        
        num_posts += 1
        if num_posts >= max_posts: break

with open("index.html", 'w') as output:
    output.write(
        template.render(
            projects=carousel,
            images=images,
            posts=features
        )
    )

# generate project pages
template = template_env.get_template('projects/projectlayout.html')

for proj, config in projs.items():
    project = ""
    name = config['name'][0]
    if 'link' in config:
        link = config['link'][0]
        
        if 'password' in link:
            project = f"<header><h3><a href={config['link'][0]}>[ Play on itch.io ]</a></h3></header>"
        elif 'itch' in link:
            project = f"<header><h3><a href={config['link'][0]}>[ Download on itch.io ]</a></h3></header>"
        elif 'garden' in link:
            project = f"<header><h3><a href={config['link'][0]}>[ Find Out More On Our Website! ]</a></h3></header>"
        else:
            project = f"<header><h3><a href={config['link'][0]}>[ View Source on GitHub ]</a></h3></header>"
    else:
        upload = config["upload"][0].strip('"')
        project = f'<header><h3>[ Play here or read more below! ]</h3><iframe frameborder="0" src="https://itch.io/embed-upload/{upload}?color=333333" allowfullscreen="" width="1200" height="675"></iframe></header>'

    with open(f"projects/posts/{name}.html", 'w') as output:
        output.write(
            template.render(
                name=name,
                banner=config['image'][0],
                project=project, 
                post=proj
            )
        )

# generate projects index
template = template_env.get_template('projects/projectslayout.html')
listitems = ["","",""] # list categories are now Personal, Collaboration, Student Work

for proj, config in projs.items():
    category = config['category'][0]
    file = f"posts/{config['name'][0]}.html"
    item = f"""\
<div class="col-4">
    <a href="{file}" class="image fit"><img src="images/{config['image'][0]}" alt="" /></a>
</div>
<div class="col-8">
    <a href="{file}"><h4>{config['name'][0]}</h4></a>
    <a href="{file}"><p>{config['summary'][0]}</p></a>
</div>\n"""

    if category == "Personal":
        listitems[0] += item
    elif category == "Collaboration":
        listitems[1] += item
    else:
        listitems[2] += item

with open("projects/projects.html", 'w') as output:
    output.write(
        template.render(
            items0=listitems[0],
            items1=listitems[1],
            items2=listitems[2],
        )
    )

# generate blog spotlight on index
