(function () {
  const data = window.WILDLIFE_DATA;
  if (!data || !data.groups) return;

  const STORAGE_KEY = 'pantanal_custom_captions_v2';
  let customCaptions = {};
  try {
    customCaptions = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch (e) {
    customCaptions = {};
  }

  const chapterNav = document.getElementById('chapter-nav');
  const collagesContainer = document.getElementById('collages-container');

  // Lightbox elements
  const lightbox = document.getElementById('lightbox-modal');
  const lbMediaHolder = document.getElementById('lb-media-holder');
  const lbStageVariants = document.getElementById('lb-stage-variants');
  const lbInfoVariants = document.getElementById('lb-info-variants');
  const lbGroupLabel = document.getElementById('lb-group-label');
  const lbSpeciesTitle = document.getElementById('lb-species-title');
  const lbCaptionText = document.getElementById('lb-caption-text');
  const lbMetaRegion = document.getElementById('lb-meta-region');
  const lbGoogleLink = document.getElementById('lb-google-link');
  const lbCloseBtn = document.getElementById('lb-close-btn');
  const lbPrevBtn = document.getElementById('lb-prev-btn');
  const lbNextBtn = document.getElementById('lb-next-btn');

  // Caption edit elements
  const lbToggleEditBtn = document.getElementById('lb-toggle-edit-btn');
  const lbEditContainer = document.getElementById('lb-edit-container');
  const lbEditTextarea = document.getElementById('lb-edit-textarea');
  const lbSaveCaptionBtn = document.getElementById('lb-save-caption-btn');
  const lbCancelCaptionBtn = document.getElementById('lb-cancel-caption-btn');

  let flatItems = [];
  let flatIndexByItemIndex = {};
  let currentLightboxIndex = -1;
  let currentVariantIndex = 0;

  function getCaption(item) {
    return customCaptions[item.index] || item.caption;
  }

  // Lazy-activate inline video playback only after images have loaded and tile is in viewport
  const videoObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const video = entry.target;
        if (entry.isIntersecting) {
          if (!video.src && video.dataset.src) {
            video.src = video.dataset.src;
          }
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      });
    },
    { threshold: 0.35 }
  );

  function createTileElement(item) {
    const flatIdx = flatIndexByItemIndex[item.index];
    const tile = document.createElement('article');
    tile.className = 'cloud-tile';
    tile.style.width = `${item.tileWidth}px`;
    tile.style.height = `${item.tileHeight}px`;
    tile.tabIndex = 0;
    tile.id = `tile-${item.index}`;
    tile.setAttribute('aria-label', `${item.species} — ${getCaption(item)}`);

    // Always render the fast custom-cropped JPEG immediately so no tile is ever blank
    const imgEl = document.createElement('img');
    imgEl.className = 'tile-img';
    imgEl.src = item.cropUrl;
    imgEl.alt = item.species;
    imgEl.decoding = 'async';
    imgEl.onerror = function () {
      if (!this.dataset.retried) {
        this.dataset.retried = '1';
        setTimeout(() => {
          this.src = item.cropUrl + '?r=1';
        }, 250);
      }
    };
    tile.appendChild(imgEl);

    const hasVariants = Array.isArray(item.variants) && item.variants.length > 1;

    if (item.isVideo) {
      const vidEl = document.createElement('video');
      vidEl.className = 'tile-video';
      vidEl.dataset.src = item.videoUrl;
      vidEl.poster = item.cropUrl;
      vidEl.muted = true;
      vidEl.loop = true;
      vidEl.playsInline = true;
      vidEl.preload = 'none';
      vidEl.style.position = 'absolute';
      vidEl.style.inset = '0';
      tile.appendChild(vidEl);

      if (!hasVariants) {
        const indicator = document.createElement('div');
        indicator.className = 'video-indicator';
        indicator.textContent = '▶';
        tile.appendChild(indicator);
      }

      videoObserver.observe(vidEl);
    }

    if (hasVariants) {
      const vIndicator = document.createElement('div');
      vIndicator.className = 'variant-indicator';
      vIndicator.textContent = `⇄ ${item.variants.length}`;
      tile.appendChild(vIndicator);
    }

    const variantBadgeHtml = hasVariants
      ? `<div class="overlay-variant-badge">⇄ ${item.variants.map((v) => v.label).join(' · ')}</div>`
      : '';

    const overlay = document.createElement('div');
    overlay.className = 'tile-caption-overlay';
    overlay.innerHTML = `
      <div class="overlay-species">${item.species}</div>
      ${variantBadgeHtml}
      <p class="overlay-caption" data-caption-index="${item.index}">${getCaption(item)}</p>
    `;
    tile.appendChild(overlay);

    tile.addEventListener('click', () => openLightbox(flatIdx, 0));
    tile.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openLightbox(flatIdx, 0);
      }
    });

    return tile;
  }

  function renderAll() {
    chapterNav.innerHTML = '';
    collagesContainer.innerHTML = '';
    flatItems = [];
    flatIndexByItemIndex = {};

    data.groups.forEach((group) => {
      group.items.forEach((item) => {
        flatIndexByItemIndex[item.index] = flatItems.length;
        flatItems.push({ item, group });
      });

      // Minimal nav pill
      const navLink = document.createElement('a');
      navLink.href = `#group-${group.id}`;
      navLink.className = 'chapter-link';
      navLink.dataset.groupId = group.id;
      navLink.textContent = group.title;
      chapterNav.appendChild(navLink);

      // Collage Section
      const section = document.createElement('section');
      section.className = 'collage-section';
      section.id = `group-${group.id}`;

      const heading = document.createElement('h2');
      heading.className = 'section-title';
      heading.textContent = group.title;
      section.appendChild(heading);

      const cloud = document.createElement('div');
      cloud.className = 'photo-cloud';

      group.cloud.forEach((colSpec) => {
        const colEl = document.createElement('div');
        colEl.className = `cloud-col align-${colSpec.align}`;
        if (colSpec.offsetY) {
          colEl.style.transform = `translateY(${colSpec.offsetY}px)`;
        }

        colSpec.slots.forEach((slot, sIdx) => {
          if (slot.type === 'pair') {
            const pairEl = document.createElement('div');
            const pairPos = sIdx === 0 ? 'pair-top' : 'pair-bottom';
            pairEl.className = `cloud-pair ${pairPos}`;
            slot.items.forEach((subItem) => {
              pairEl.appendChild(createTileElement(subItem));
            });
            colEl.appendChild(pairEl);
          } else {
            colEl.appendChild(createTileElement(slot.item));
          }
        });

        cloud.appendChild(colEl);
      });

      section.appendChild(cloud);
      collagesContainer.appendChild(section);
    });

    setupScrollSpy();
  }

  function getActiveVariantObject(item) {
    if (Array.isArray(item.variants) && item.variants.length > 1) {
      return item.variants[currentVariantIndex] || item.variants[0];
    }
    return item;
  }

  function renderLightboxVariant(vIdx) {
    if (currentLightboxIndex < 0 || currentLightboxIndex >= flatItems.length) return;
    const { item, group } = flatItems[currentLightboxIndex];
    const hasVariants = Array.isArray(item.variants) && item.variants.length > 1;
    currentVariantIndex = hasVariants ? Math.max(0, Math.min(vIdx, item.variants.length - 1)) : 0;

    const activeObj = getActiveVariantObject(item);

    lbGroupLabel.textContent = group.title;
    lbSpeciesTitle.textContent = activeObj.species || item.species;
    lbCaptionText.textContent = getCaption(activeObj);
    lbMetaRegion.textContent = `${activeObj.region} · ${activeObj.date}`;
    if (activeObj.index === 426) {
      lbGoogleLink.href = activeObj.photoUrl;
    } else if ([425, 427, 428, 429, 430, 431, 433, 434, 435].includes(activeObj.index)) {
      lbGoogleLink.href = 'https://photos.app.goo.gl/7zzDVY2vMUL3mQhm6';
    } else {
      lbGoogleLink.href = `https://photos.google.com/share/AF1QipPqr8g8Zyc2JpTkgOB8ZXkqDgVu_L8GaxUfrZ9yESs6NeJppagzIptASC8BF7L-Cw/photo/${activeObj.id}?key=MDdtYTlzbjhnWkJLcW94QXJmelpCaWtSV05DbkxB`;
    }

    lbEditContainer.classList.remove('open');
    lbEditTextarea.value = getCaption(activeObj);

    // Update variant toggle buttons in both stage and info sidebar
    [lbStageVariants, lbInfoVariants].forEach((container) => {
      if (!container) return;
      container.innerHTML = '';
      if (hasVariants) {
        container.classList.add('visible');
        item.variants.forEach((v, idx) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = `lb-variant-btn${idx === currentVariantIndex ? ' active' : ''}`;
          btn.setAttribute('role', 'tab');
          btn.setAttribute('aria-selected', idx === currentVariantIndex ? 'true' : 'false');
          btn.textContent = v.isVideo ? `▶ ${v.label}` : v.label;
          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (currentVariantIndex !== idx) {
              renderLightboxVariant(idx);
            }
          });
          container.appendChild(btn);
        });
      } else {
        container.classList.remove('visible');
      }
    });

    lbMediaHolder.innerHTML = '';
    if (activeObj.isVideo) {
      const vid = document.createElement('video');
      vid.src = activeObj.videoUrl;
      vid.poster = activeObj.photoUrl;
      vid.controls = true;
      vid.autoplay = true;
      vid.playsInline = true;
      lbMediaHolder.appendChild(vid);
    } else {
      const img = document.createElement('img');
      img.src = activeObj.photoUrl;
      img.alt = `${activeObj.species || item.species}${activeObj.label ? ' — ' + activeObj.label : ''}`;
      lbMediaHolder.appendChild(img);
    }
  }

  function openLightbox(flatIdx, variantIdx = 0) {
    if (flatIdx < 0 || flatIdx >= flatItems.length) return;
    currentLightboxIndex = flatIdx;
    renderLightboxVariant(variantIdx);
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('open');
    lbMediaHolder.innerHTML = '';
    document.body.style.overflow = '';
    currentLightboxIndex = -1;
    currentVariantIndex = 0;
  }

  lbCloseBtn.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  lbPrevBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const prev = (currentLightboxIndex - 1 + flatItems.length) % flatItems.length;
    openLightbox(prev, 0);
  });

  lbNextBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const next = (currentLightboxIndex + 1) % flatItems.length;
    openLightbox(next, 0);
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('open')) return;
    if (document.activeElement === lbEditTextarea) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') lbPrevBtn.click();
    if (e.key === 'ArrowRight') lbNextBtn.click();
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      const { item } = flatItems[currentLightboxIndex] || {};
      if (item && Array.isArray(item.variants) && item.variants.length > 1) {
        e.preventDefault();
        const nextVar = (currentVariantIndex + 1) % item.variants.length;
        renderLightboxVariant(nextVar);
      }
    }
  });

  lbToggleEditBtn.addEventListener('click', () => {
    lbEditContainer.classList.toggle('open');
    if (lbEditContainer.classList.contains('open')) {
      lbEditTextarea.focus();
    }
  });

  lbCancelCaptionBtn.addEventListener('click', () => {
    lbEditContainer.classList.remove('open');
  });

  lbSaveCaptionBtn.addEventListener('click', () => {
    if (currentLightboxIndex < 0) return;
    const { item } = flatItems[currentLightboxIndex];
    const activeObj = getActiveVariantObject(item);
    const newText = lbEditTextarea.value.trim();
    if (newText) {
      customCaptions[activeObj.index] = newText;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(customCaptions));
      lbCaptionText.textContent = newText;
      const tileCaption = document.querySelector(`[data-caption-index="${activeObj.index}"]`);
      if (tileCaption) tileCaption.textContent = newText;
    }
    lbEditContainer.classList.remove('open');
  });

  function setupScrollSpy() {
    const sections = document.querySelectorAll('.collage-section');
    const navLinks = document.querySelectorAll('.chapter-link');
    if (!sections.length) return;

    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace('group-', '');
            navLinks.forEach((link) => {
              link.classList.toggle('active', link.dataset.groupId === id);
            });
          }
        });
      },
      { rootMargin: '-30% 0px -60% 0px' }
    );

    sections.forEach((s) => spy.observe(s));
  }

  renderAll();
})();
