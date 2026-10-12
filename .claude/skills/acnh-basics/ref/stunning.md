# What makes ACNH islands look stunning: concrete findings

**Source limits.** Reddit (r/ACQR, r/AnimalCrossing) and Xiaohongshu were blocked to the fetch tools. Reddit-origin tips below come through articles that credit the Redditor. No source gives measured item totals for a top island. The hard numbers are the game's rating thresholds, creator-reported counts, and lag reports. Item names were checked against `designs/acnh_catalog.json`, with sizes in tiles.

## 1. Density (numbers)

| Fact | Value | Source |
|---|---|---|
| Rating clutter cap | More than 45 items in any 8×8 area caps the island at 4★ | https://chibisnorlax.github.io/acnhfaq/island-dev/rating/ |
| Same-item penalty | More than 6 of the same item in an 8×8 area costs points | same |
| Tree cap | More than 220 trees/shrubs caps the island at 4★ | same |
| Dropped-item cap | 15 or more dropped items caps the island at 4★ | same |
| Acre size / island size | 16×16 tiles per acre; island is 5×4 acres | https://www.belltreeforums.com/threads/can-too-much-placed-furniture-count-as-clutter.579354/ ; https://news.17173.com/z/dwsyh/content/02182021/015017667.shtml |
| Small shop vignette (Japanese creator) | 10×10 plot, 4×6 raised cliff base; 3–4 **stall**, 2 **simple panel**, ≥6 one-tile props, ≥4 floor items, about 20 customization kits, so roughly 15–20 items on about 24 tiles | https://a-nosuri.com/blog-entry-896.html |
| Small rest spot | 5×5: only 1–2 tall items, low props at the front and corners | https://www.lemon8-app.com/experience/%E3%81%82%E3%81%A4%E6%A3%AE-%E5%B3%B6%E3%82%AF%E3%83%AA%E3%82%A8%E3%82%A4%E3%82%BF%E3%83%BC-%E5%8F%82%E8%80%83?region=jp |
| Cliff-top planter | Tree needs 3×3; 1-tile flowers/shrubs fill the edge | https://kokorogu.com/atumori-63 |
| Ground coverage report | One island covered about 85% of its ground with the clover custom design; lag appeared only at waterfalls and Resident Services | https://belltreeforums.com/threads/frame-rate-science.640259/ |

**Takeaway.** Showcase vignettes hold about 0.6–1 item per tile, which breaks the 45-per-8×8 rule. Dream islands like Porthaven ("nearly every inch covered in vegetation") give up 5★ (https://screenrant.com/animal-crossing-best-island-designs-2024/).

**Lag comes from animated items, not item count.** The heavy items are bubble machines, stage/floor lights, conveyor belts, tin robots, teacups, arcade machines, and clustered gyroids. Four-tile waterfalls also lag; cutting them to three tiles fixed it. Flowers showed no visible lag (https://belltreeforums.com/threads/frame-rate-science.640259/). Confetti machines in one area also caused lag, and players report lag after placing many simple panels (https://xsionx.com/animal-crossing/post-11718/ ; https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q12224036127).

**Workflow limits.**
- Catalog orders are limited to 5 items per day; Natto called this the biggest bottleneck. His Fushimi Inari build took 11 days, and his Utsusemi Island had over 10,000 dream visits (https://automaton-media.com/en/news/20211127-6683/).
- Design slots: 90 normal + 90 pro, as of 1.9.0 (https://nookipedia.com/wiki/Custom_design). Chinese guidance is to avoid any ground set that needs more than 6 slots (https://www.gamersky.com/handbook/202005/1285333.shtml).

## 2. Ground work

- **Preset paths look man-made.** Their crisp edges "read as constructed." Fix this with semi-transparent dirt custom designs that let grass show through (https://www.switchbladegaming.com/cozy-games/animal-crossing-island-design-guide/).
- **Denim2's 9-piece dirt set** (MA-6647-9230-4716) has rough, star-cut edges and uses transparency (https://animalcrossingworld.com/2020/06/these-amazing-dirt-pathway-patterns-are-taking-over-the-animal-crossing-new-horizons-community/).
- **Wrap trick.** Leave one transparent pixel in a design and it wraps to the shape of the Island Designer path underneath, so one tile handles corners. Test it over different base paths (https://www.thegamer.com/animal-crossing-new-horizons-wrap-paths-custom-designs-simple-trick/ ; https://altema.jp/atsumori/koteika).
- **Layer the paths.**
  - Lay a base path, then add "circle" and "broken stone" variants for wear (https://leialeilani.com/guides/island-path-and-decorating-guide).
  - A Nebula path over dark dirt looks worn (https://twinfinite.net/guides/animal-crossing-new-horizons-best-path-custom-designs/).
  - Layer a design over a real path so footstep sounds match the surface (https://news.17173.com/z/dwsyh/content/02182021/015017667.shtml).
- **Edges and texture.**
  - Grass-overhang edge designs (ナジマセソウ), moss for cobbles, and fallen-leaf scatters (https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q10277054955).
  - Draw edge pieces (top, bottom, left, right) for realism (https://altema.jp/atsumori/mydesignmichi).
  - A brick-edge strip along brick paths (https://www.mymeblog.com/entry/2022/01/05/134304).
- **Plants as texture.**
  - Weeds, flowers, bushes, and patterns mixed together to fill gaps.
  - Baby pines and oaks used as fake weeds.
  - Lilies mixed with hyacinths (https://www.belltreeforums.com/threads/show-me-how-you-fill-empty-space-on-your-islands.580991/ ; https://www.belltreeforums.com/threads/please-help-me-and-give-me-ideas-to-make-my-island-look-prettier.496427/).
- **Plain grass.** Forum critique says open areas with nothing in them look unfinished (https://www.belltreeforums.com/threads/island-feedback-and-showcase-thread.590229/). Some bare grass is still needed between zones; otherwise the island reads like a "floor-tile showroom" (Switchblade).

## 3. Verticality and terrain

- **Limits.** 8 inclines and 8 bridges. Cliffs go 4 tiers high, but items can't be placed on the top tier, so creators use 3 (https://note.com/reitouko/n/ne12518ef7698 ; https://kokorogu.com/atumori-63).
- **Waterfalls.** The minimum cliff is 2×3; 3×3 is better (https://hakusai-games.hatenablog.jp/entry/Island-creator_5-points). Waterfalls 3 tiles wide or narrower avoid lag (Bell Tree).
- **Cliffs as facades.**
  - Lines of simple panels "disguise walls and hide cliffs"; stacked panels fake doors (https://www.douban.com/group/topic/175933326/ ; https://www.gamersky.com/handbook/202005/1285333.shtml).
  - A cliff 2 tiles behind a stall hides its back (a-nosuri).
  - A ring of cliffs around a building splits sightlines between districts (GamerSky).
- **Placement detail.**
  - Put the focal building on tier 2–3 with ramps leading up (Bell Tree, Luca).
  - Put 1-tile flowers or shrubs on the cliff-top edge (kokorogu).
  - Mix round and square edges; all-square cliffs look too urban (GamerSky).
- **Rivers.**
  - Use diagonals and uneven widths, or add a 1-tile islet (hakusai).
  - Straight channels "look like drainage ditches"; cascades over 2–3 tiers work best (Switchblade).
  - Leave some weedy bank (https://madfandom.com/acnh-river-ideas/).

## 4. Composition for the camera

- **Height order.** Tall items go at the back (north). Height should rise from front to back, with gaps between trees for depth (https://hakusai-games.hatenablog.jp/entry/Island-creator_5-points).
- **Two viewpoints.**
  - Looking up from tier 1: the hero item sits on the cliff, with no tall items in the foreground.
  - Looking down from tier 2–3: a walled "box garden" (same source).
- **Framing.**
  - Design for the widest Pro Camera zoom at mid-distance.
  - Hide a view behind a narrow passage so it opens up suddenly (https://note.com/reitouko/n/ne12518ef7698).
  - A lower camera angle adds depth to street scenes (https://www.mymeblog.com/entry/2020/09/10/161750).
- **Variety.** Don't line up many of the same item; use asymmetry. For gardens, use **garden rock** + **tall garden rock** + shrubs (Natto, https://automaton-media.com/en/news/20211127-6683/).
- **Night.**
  - Neon signs, spotlights, and floor lights stay lit by day; illumination items only light at night.
  - Dense rows of one lamp in graded colors.
  - Dollhouses plus a running projector or blinking server in the far background suggest a city skyline (https://a-nosuri.com/blog-entry-1068.html).
  - The Showa street was shown at night to stress clutter (https://kotaku.com/retro-japan-recreated-in-animal-crossing-new-horizons-1843018248).

## 5. City / London / European streets

**Techniques**
- **Façades.** Stack customized **simple panel** (1×0.5) against cliffs on several elevation levels to make skyscrapers and shopfronts. Use **stall** (2×1) for shop counters, subway roofs, and ticket booths (https://www.fandomspot.com/acnh-urban-island-ideas/ ; https://www.tiktok.com/discover/%E3%81%82%E3%81%A4%E6%A3%AE-%E3%83%AD%E3%83%B3%E3%83%89%E3%83%B3%E9%A2%A8).
- **Shop door recipe.**
  - Two white **simple panel** pieces flush against the cliff.
  - A 1-tile appliance on each side (vending machine, fridge) to hide cliff soil.
  - Grey paving and **medium cardboard boxes** (ひっこしダンボールM) (a-nosuri).
- **Partitions.** The HHP "partition wall" is interior-only (https://nookipedia.com/wiki/Item:Partition_wall_(New_Horizons)). Outdoors, use furniture partitions instead (**wood partition** 2×0.5, **medium wooden partition**), **castle wall** (2×1, customizable, outdoor-only), and **short simple panel** (catalog).
- **Roads.**
  - Lay an Island Designer path, then an edged brick design on top, for an urban look. Diagonal brick is done with custom designs (https://game8.jp/atsumare-doubutsunomori/331282).
  - Street-line, crosswalk, pothole, and sewer-grate designs (fandomspot).
  - Cobblestone in greige; 9-piece uneven-brick sets for curves (https://atsumori-mydesign.com/european-style-cityscape/).
  - **iron-and-stone fence** (ようふうのさく) along a canal (https://www.mymeblog.com/entry/2020/05/27/164948).
- **Grit.** Trash bags, tin buckets, cardboard boxes, and overgrowth (fandomspot). Showa-era ad signs and jammed storefronts (Kotaku). Telephone poles, rock gardens, and vending machines for a Shibuya street (https://www.dexerto.com/animal-crossing/top-5-best-town-layouts-in-animal-crossing-new-horizons-1355827/).

**Item list (catalog-verified)**
- Façades and walls: simple panel, short simple panel, castle wall, stall, construction scaffolding, iron frame
- Lighting: streetlamp, round streetlight, curved streetlight, street lamp with banners
- Street fixtures: manhole cover, fire hydrant, utility pole, phone box, crosswalk signal, plaza clock, park clock
- Signs: standing shop sign, plain wooden shop sign, backlit sign, diner neon sign
- Benches: public bench, plaza bench, outdoor bench
- Utilities and clutter: garbage bin, trash bags, outdoor air conditioner, outdoor generator, cruiser bike
- Fences: iron fence, iron-and-stone fence, brick fence, block fence
- Greenery: hedge, hedge standee

## 6. Countryside / cottagecore

**Techniques**
- Semi-transparent dirt paths over grass (Switchblade).
- Flowers in 3×3 grids with gaps.
- A greenhouse built from two **stall** + one **simple panel** (https://www.fandomspot.com/acnh-cottagecore-ideas/ ; https://thefriendlyfig.com/2026/03/16/cottagecore-animal-crossing-island/).
- Lanterns on **barrel** or **log stool**, arranged "messy yet organized."
- Weeds planted into small gaps (https://www.goldkk.com/news/1928--best-acnh-cottagecore-design-ideas-animal-crossing-island-design-tips).
- One square of barbed-wire fence or a half-ring of fence around a tree; **firewood** beside trees; **wooden bucket** near water (Bell Tree fill-space thread).

**Item list (catalog-verified)**
- Laundry and household: clothesline, garden wagon, hay bed, firewood, log stakes
- Farm and water: water pump, simple well, brick well, scarecrow, wooden bucket, tin bucket, handcart
- Flowers and garden: flower bed, flower stand, pergola, stone arch
- Fences: country fence, corral fence, simple wooden fence, log fence
- Seating: garden bench, log bench, log stool
- Lighting: garden lantern

Mush items and the ironwood kitchenette also appear in these builds (https://www.fandomspot.com/acnh-cottagecore-ideas/).

## 7. Why islands look boring (designer critiques)

1. **Wide paths.** They read as "long, empty plazas." Use 4 tiles for main streets and 2–3 for minor paths (https://www.belltreeforums.com/threads/please-help-me-and-give-me-ideas-to-make-my-island-look-prettier.496427/).
2. **Straight geometry and perfect alignment**, with cliffs only along the top of the map (same thread). Straight rivers look like ditches (Switchblade).
3. **Repeating one item or pattern instead of using asymmetry** (Natto). Huge flower grids read as tiling (https://www.gamersky.com/handbook/202004/1280005.shtml).
4. **Flat ground with untouched grass and hard-edged preset paths** (Switchblade; Bell Tree showcase thread).
5. **Crowding without hierarchy.** Too many tall items, or stacked trees blocking the view (hakusai; Lemon8).
6. **Clustered buildings, mismatched paths, bridges, and fences, wild flowers, and orchards** (https://www.thegamer.com/animal-crossing-tips-beginner-mistakes-island-design/).
7. **Every zone at the same density.** Alternate dense markets with quieter breathing zones (https://acnhchill.com/animal-crossing-new-horizons-full-guide/island-design/island-zoning-neighborhood-structure/).
