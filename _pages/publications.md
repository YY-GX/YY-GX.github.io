---
layout: pub_page
permalink: /publications/
title: Publications
realtitle: Publications and Preprints
description: Publications and preprints by categories in reversed chronological order. 
years: [2024, 2022, 2020]
nav: true
nav_order: 1
---
<!-- _pages/publications.md -->
<div class="publications">

{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
