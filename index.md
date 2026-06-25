---
layout: default
title: Home
---

## Welcome to my digital workshop

This is where I document my thoughts, deep dives into various hobbies, and whatever else I happen to be experimenting with at the moment. 

### Latest Posts
<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a> — <span>{{ post.date | date: "%b %d, %Y" }}</span>
    </li>
  {% endfor %}
</ul>
