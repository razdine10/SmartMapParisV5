/* global mapboxgl, MAPBOX_TOKEN */

mapboxgl.accessToken = MAPBOX_TOKEN;

const DEFAULT_VIEW = { center: [2.3522, 48.8566], zoom: 11.2, pitch: 45, bearing: -17.6 };
const FRANCE_VIEW = { center: [2.5, 46.7], zoom: 4.6, pitch: 45, bearing: -10 };

const map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/mapbox/light-v11',
	center: DEFAULT_VIEW.center,
	zoom: DEFAULT_VIEW.zoom,
	pitch: DEFAULT_VIEW.pitch,
	bearing: DEFAULT_VIEW.bearing,
	antialias: true,
});

map.addControl(new mapboxgl.NavigationControl());

// Enhanced zoom controls
map.doubleClickZoom.disable();
map.on('dblclick', (e) => {
	map.easeTo({ center: e.lngLat, zoom: map.getZoom() + 2.5, duration: 320 });
});

map.on('contextmenu', (e) => {
	// Right click: strong zoom
	map.easeTo({ center: e.lngLat, zoom: map.getZoom() + 3.5, duration: 380 });
});

// Left click: zoom (ignore if double-click)
map.on('click', (e) => {
	const ev = e.originalEvent;
	if (ev && ev.detail && ev.detail > 1) return; // Avoid stacking with double-click
	map.easeTo({ center: e.lngLat, zoom: map.getZoom() + 2.0, duration: 300 });
});

map.on('error', (e) => {
	console.error('Map error:', e && e.error ? e.error : e);
});



function getColorForPrice(price) {
	if (!price || price === null) return 'rgba(59, 130, 246, 0.45)';
	if (price <= 1000) return 'rgba(0, 61, 122, 0.5)';
	if (price <= 1500) return 'rgba(0, 102, 204, 0.5)';
	if (price <= 2500) return 'rgba(0, 153, 255, 0.5)';
	if (price <= 3500) return 'rgba(0, 204, 255, 0.5)';
	if (price <= 5000) return 'rgba(0, 255, 204, 0.5)';
	if (price <= 7000) return 'rgba(102, 255, 0, 0.5)';
	if (price <= 9000) return 'rgba(204, 255, 0, 0.5)';
	if (price <= 11000) return 'rgba(255, 204, 0, 0.5)';
	if (price <= 13000) return 'rgba(255, 102, 0, 0.5)';
	return 'rgba(204, 0, 0, 0.5)';
}

function getBorderColorForPrice(price) {
	if (!price || price === null) return 'rgba(59, 130, 246, 0.7)';
	if (price <= 1000) return 'rgba(0, 61, 122, 0.75)';
	if (price <= 1500) return 'rgba(0, 102, 204, 0.75)';
	if (price <= 2500) return 'rgba(0, 153, 255, 0.75)';
	if (price <= 3500) return 'rgba(0, 204, 255, 0.75)';
	if (price <= 5000) return 'rgba(0, 255, 204, 0.75)';
	if (price <= 7000) return 'rgba(102, 255, 0, 0.75)';
	if (price <= 9000) return 'rgba(204, 255, 0, 0.75)';
	if (price <= 11000) return 'rgba(255, 204, 0, 0.75)';
	if (price <= 13000) return 'rgba(255, 102, 0, 0.75)';
	return 'rgba(204, 0, 0, 0.75)';
}

function attachHover(layerId) {
	if (!map.getLayer(layerId)) return;

	map.off('mousemove', layerId, map._hoverHandler);
	map.off('mouseleave', layerId, map._leaveHandler);
	map._hoverHandler = (e) => {
		map.getCanvas().style.cursor = 'pointer';
		if (!e.features || !e.features[0]) return;
		const p = e.features[0].properties;
		const name = p.name || p.l_ar || p.nom || '';
		const price = p.avg_price_m2 ? Number(p.avg_price_m2).toLocaleString('fr-FR') + ' €/m²' : 'N/A';
		const transactions = p.transaction_count ? Number(p.transaction_count).toLocaleString('fr-FR') + ' transactions' : 'N/A';
		

		const bgColor = getColorForPrice(p.avg_price_m2);
		const borderColor = getBorderColorForPrice(p.avg_price_m2);
		
		const html = `
			<div class="hover-card" style="background: ${bgColor}; border-color: ${borderColor};">
				<div class="hc-title">${name}</div>
				<div class="hc-row"><div class="hc-icon">💶</div><div class="hc-price">${price}</div></div>
				<div class="hc-row"><div class="hc-icon">📊</div><div class="hc-tx">${transactions}</div></div>
			</div>
		`;
		if (!window._tooltip) window._tooltip = new mapboxgl.Popup({ closeButton: false, closeOnClick: false, className: 'hover-popup', offset: 12 });
		window._tooltip.setLngLat(e.lngLat).setHTML(html).addTo(map);
	};
	map._leaveHandler = () => {
		map.getCanvas().style.cursor = '';
		if (window._tooltip) window._tooltip.remove();
	};
	map.on('mousemove', layerId, map._hoverHandler);
	map.on('mouseleave', layerId, map._leaveHandler);
}

document.getElementById('reset-view')?.addEventListener('click', () => {
	const mode = document.getElementById('mode-select')?.value || 'paris';
	const view = mode === 'france' ? FRANCE_VIEW : DEFAULT_VIEW;
	map.easeTo({ ...view, duration: 800 });
});

async function fetchYears() {
	const res = await fetch('/api/years/');
	const data = await res.json();
	return data.years || [];
}

async function fetchParisPrices(year) {
	const res = await fetch(`/api/prices/?year=${year}`);
	return await res.json();
}

async function fetchParisArr() {
	const res = await fetch('/api/arrondissements/');
	return await res.json();
}

async function fetchFrancePrices(year) {
	const res = await fetch(`/api/france/prices/?year=${year}`);
	return await res.json();
}

async function fetchDepartements() {
	const res = await fetch('/api/france/departements/');
	return await res.json();
}

async function fetchQuartiersPrices(year) {
	const res = await fetch(`/api/quartiers/prices/?year=${year}`);
	return await res.json();
}

async function fetchQuartiers() {
	const res = await fetch('/api/quartiers/');
	return await res.json();
}

function mapStatsByCode(statsData, codeProp) {
	const byCode = new Map();
	// Handle both old FeatureCollection format and new data format
	const dataArray = statsData.features || statsData.data || [];
	for (const item of dataArray) {
		const data = item.properties || item;
		const code = data[codeProp];
		byCode.set(String(code), data);
	}
	return byCode;
}

function createColorExpression() {
	return [
		'interpolate',
		['linear'],
		['coalesce', ['get', 'avg_price_m2'], 1000],
		1000, '#003d7a',
		1500, '#0066CC',
		2500, '#0099FF',
		3500, '#00CCFF',
		5000, '#00FFCC',
		7000, '#66FF00',
		9000, '#CCFF00',
		11000, '#FFCC00',
		13000, '#FF6600',
		15000, '#CC0000'
	];
}



function updateLegend(min, max) {
	const bar = document.getElementById('legend-bar');
	const minEl = document.getElementById('legend-min');
	const maxEl = document.getElementById('legend-max');
	if (!bar || !minEl || !maxEl) return;
	
	const gradient = [
		'linear-gradient(to right',
		'#003d7a 0%',
		'#0066CC 12%',
		'#0099FF 25%',
		'#00CCFF 37%',
		'#00FFCC 50%',
		'#66FF00 62%',
		'#CCFF00 75%',
		'#FFCC00 87%',
		'#FF6600 95%',
		'#CC0000 100%)'
	].join(', ');
	
	bar.style.background = gradient;
	minEl.textContent = `${Math.round(min).toLocaleString('fr-FR')} €/m²`;
	maxEl.textContent = `${Math.round(max).toLocaleString('fr-FR')} €/m²`;
}

async function renderParis(year) {
	const [arrGeo, stats] = await Promise.all([
		fetchParisArr(),
		fetchParisPrices(year),
	]);
	const statsByCode = mapStatsByCode(stats, 'arrondissement_code');
	for (const feature of arrGeo.features) {
		const codeInsee = String(feature.properties.c_arinsee).padStart(5, '0');
		const stat = statsByCode.get(codeInsee);
		feature.properties.avg_price_m2 = stat ? stat.avg_price_m2 : null;
		feature.properties.transaction_count = stat ? stat.transaction_count : null;
		feature.properties.name = feature.properties.l_ar;
	}
	const prices = arrGeo.features.map(f => f.properties.avg_price_m2).filter(v => v != null);
	let min = 700, max = 150000;
	if (prices.length) { 
		const dataMin = Math.min(...prices); 
		const dataMax = Math.max(...prices); 
	
		min = Math.max(700, dataMin - 500);
		max = Math.min(150000, dataMax + 2000);
		if (min === max) max = min + 1000;
	}
	updateLegend(min, max);

	const heightExpression = ['case', ['to-boolean', ['get', 'avg_price_m2']], ['/', ['get', 'avg_price_m2'], 90], 0];
	const colorExpression = createColorExpression();


	if (map.getLayer('dept-extrusion')) map.removeLayer('dept-extrusion');
	if (map.getSource('dept')) map.removeSource('dept');
	if (map.getLayer('dept-outline')) map.removeLayer('dept-outline');
	if (map.getSource('dept-outline-src')) map.removeSource('dept-outline-src');


	if (!map.getSource('arr-outline-src')) {
		map.addSource('arr-outline-src', { type: 'geojson', data: arrGeo });
		map.addLayer({ id: 'arr-outline', type: 'line', source: 'arr-outline-src', paint: { 'line-color': '#2c3e50', 'line-width': 1 } });
	} else {
		map.getSource('arr-outline-src').setData(arrGeo);
	}


	if (!map.getSource('arr')) {
		map.addSource('arr', { type: 'geojson', data: arrGeo });
		map.addLayer({ 
			id: 'arr-extrusion', 
			type: 'fill-extrusion', 
			source: 'arr', 
			paint: { 
				'fill-extrusion-height': heightExpression, 
				'fill-extrusion-color': colorExpression, 
				'fill-extrusion-opacity': 0.7, 
				'fill-extrusion-vertical-gradient': true 
			} 
		});
	} else {
		map.getSource('arr').setData(arrGeo);
		map.setPaintProperty('arr-extrusion', 'fill-extrusion-height', heightExpression);
		map.setPaintProperty('arr-extrusion', 'fill-extrusion-color', colorExpression);
	}
	attachHover('arr-extrusion');
}

async function renderFrance(year) {
	const [deptGeo, stats] = await Promise.all([
		fetchDepartements(),
		fetchFrancePrices(year),
	]);
	const statsByCode = mapStatsByCode(stats, 'department_code');
	for (const feature of deptGeo.features) {
		const code = String(feature.properties.code);
		const stat = statsByCode.get(code);
		feature.properties.avg_price_m2 = stat ? stat.avg_price_m2 : null;
		feature.properties.transaction_count = stat ? stat.transaction_count : null;
		feature.properties.name = feature.properties.nom;
	}
	const prices = deptGeo.features.map(f => f.properties.avg_price_m2).filter(v => v != null);
	let min = 1000, max = 15000;
	if (prices.length) { 
		const dataMin = Math.min(...prices); 
		const dataMax = Math.max(...prices); 
	
		min = Math.max(1000, dataMin - 200);
		max = Math.min(15000, dataMax + 1000);
		if (min === max) max = min + 500;
	}
	updateLegend(min, max);

	const heightExpression = ['case', ['to-boolean', ['get', 'avg_price_m2']], ['/', ['get', 'avg_price_m2'], 60], 0];
	const colorExpression = createColorExpression();


	if (map.getLayer('arr-extrusion')) map.removeLayer('arr-extrusion');
	if (map.getSource('arr')) map.removeSource('arr');
	if (map.getLayer('arr-outline')) map.removeLayer('arr-outline');
	if (map.getSource('arr-outline-src')) map.removeSource('arr-outline-src');


	if (!map.getSource('dept-outline-src')) {
		map.addSource('dept-outline-src', { type: 'geojson', data: deptGeo });
		map.addLayer({ id: 'dept-outline', type: 'line', source: 'dept-outline-src', paint: { 'line-color': '#2c3e50', 'line-width': 0.8 } });
	} else {
		map.getSource('dept-outline-src').setData(deptGeo);
	}


	if (!map.getSource('dept')) {
		map.addSource('dept', { type: 'geojson', data: deptGeo });
		map.addLayer({ 
			id: 'dept-extrusion', 
			type: 'fill-extrusion', 
			source: 'dept', 
			paint: { 
				'fill-extrusion-height': heightExpression, 
				'fill-extrusion-color': colorExpression, 
				'fill-extrusion-opacity': 0.7, 
				'fill-extrusion-vertical-gradient': true 
			} 
		});
	} else {
		map.getSource('dept').setData(deptGeo);
		map.setPaintProperty('dept-extrusion', 'fill-extrusion-height', heightExpression);
		map.setPaintProperty('dept-extrusion', 'fill-extrusion-color', colorExpression);
	}
	attachHover('dept-extrusion');
}

async function renderQuartiers(year) {
	const [quartiersGeo, stats] = await Promise.all([
		fetchQuartiers(),
		fetchQuartiersPrices(year),
	]);
	
	const statsByCode = mapStatsByCode(stats, 'quartier_code');
	for (const feature of quartiersGeo.features) {
		const code = String(feature.properties.c_qu);
		const stat = statsByCode.get(code);
		feature.properties.avg_price_m2 = stat ? stat.avg_price_m2 : null;
		feature.properties.transaction_count = stat ? stat.transaction_count : null;
		feature.properties.name = stat ? stat.full_name : (feature.properties.l_qu || feature.properties.nom);
	}
	
	const prices = quartiersGeo.features.map(f => f.properties.avg_price_m2).filter(v => v != null);
	let min = 500, max = 200000;
	if (prices.length) { 
		const dataMin = Math.min(...prices); 
		const dataMax = Math.max(...prices); 
	
		min = Math.max(500, dataMin - 1000);
		max = Math.min(200000, dataMax + 3000);
		if (min === max) max = min + 1000;
	}
	updateLegend(min, max);

	const heightExpression = ['case', ['to-boolean', ['get', 'avg_price_m2']], ['/', ['get', 'avg_price_m2'], 120], 0];
	const colorExpression = createColorExpression();

	// Remove existing layers
	if (map.getLayer('arr-extrusion')) map.removeLayer('arr-extrusion');
	if (map.getSource('arr')) map.removeSource('arr');
	if (map.getLayer('arr-outline')) map.removeLayer('arr-outline');
	if (map.getSource('arr-outline-src')) map.removeSource('arr-outline-src');
	if (map.getLayer('dept-extrusion')) map.removeLayer('dept-extrusion');
	if (map.getSource('dept')) map.removeSource('dept');
	if (map.getLayer('dept-outline')) map.removeLayer('dept-outline');
	if (map.getSource('dept-outline-src')) map.removeSource('dept-outline-src');

	// Add quartiers outline
	if (!map.getSource('quartiers-outline-src')) {
		map.addSource('quartiers-outline-src', { type: 'geojson', data: quartiersGeo });
		map.addLayer({ id: 'quartiers-outline', type: 'line', source: 'quartiers-outline-src', paint: { 'line-color': '#2c3e50', 'line-width': 0.8 } });
	} else {
		map.getSource('quartiers-outline-src').setData(quartiersGeo);
	}

	// Add quartiers extrusion
	if (!map.getSource('quartiers')) {
		map.addSource('quartiers', { type: 'geojson', data: quartiersGeo });
		map.addLayer({ 
			id: 'quartiers-extrusion', 
			type: 'fill-extrusion', 
			source: 'quartiers', 
			paint: { 
				'fill-extrusion-height': heightExpression, 
				'fill-extrusion-color': colorExpression, 
				'fill-extrusion-opacity': 0.7, 
				'fill-extrusion-vertical-gradient': true 
			} 
		});
	} else {
		map.getSource('quartiers').setData(quartiersGeo);
		map.setPaintProperty('quartiers-extrusion', 'fill-extrusion-height', heightExpression);
		map.setPaintProperty('quartiers-extrusion', 'fill-extrusion-color', colorExpression);
	}
	attachHover('quartiers-extrusion');
}

async function render(mode, year) {
	let modeName = 'Paris';
	if (mode === 'france') modeName = 'France';
	else if (mode === 'quartiers') modeName = 'Quartiers de Paris';

	document.getElementById('current-mode').textContent = modeName;
	document.getElementById('current-year').textContent = year || '---';
	
	if (mode === 'france') {
		map.easeTo({ ...FRANCE_VIEW, duration: 800 });
		await renderFrance(year);
	} else if (mode === 'quartiers') {
		map.easeTo({ ...DEFAULT_VIEW, duration: 800 });
		await renderQuartiers(year);
	} else {
		map.easeTo({ ...DEFAULT_VIEW, duration: 800 });
		await renderParis(year);
	}
}

async function init() {
	const years = await fetchYears();
	const modeSelect = document.getElementById('mode-select');
	const yearSelect = document.getElementById('year-select');
	const themeSelect = document.getElementById('theme-select');
	

	yearSelect.innerHTML = '';
	if (years.length === 0) {
		yearSelect.innerHTML = '<option value="">Aucune donnée</option>';
		return;
	}
	
	years.forEach(y => { 
		const opt = document.createElement('option'); 
		opt.value = String(y); 
		opt.textContent = y; 
		yearSelect.appendChild(opt); 
	});
	
	const defaultYear = years.includes(2024) ? 2024 : years[years.length - 1];
	yearSelect.value = String(defaultYear);
	

	let modeName = 'Paris';
	if (modeSelect.value === 'france') modeName = 'France';
	else if (modeSelect.value === 'quartiers') modeName = 'Quartiers de Paris';
	document.getElementById('current-mode').textContent = modeName;
	document.getElementById('current-year').textContent = defaultYear;

	
	const updateMap = () => render(modeSelect.value, Number(yearSelect.value));
	

	const changeTheme = () => {
		const newStyle = themeSelect.value;
		map.setStyle(newStyle);

		map.once('style.load', () => render(modeSelect.value, Number(yearSelect.value)));
	};

	modeSelect.addEventListener('change', updateMap);
	yearSelect.addEventListener('change', updateMap);
	themeSelect.addEventListener('change', changeTheme);
	document.getElementById('reset-view').addEventListener('click', () => {
		const mode = modeSelect.value;
		const view = mode === 'france' ? FRANCE_VIEW : DEFAULT_VIEW;
		map.easeTo(view);
	});


	if (map.loaded()) {
		render(modeSelect.value, Number(defaultYear));
	} else {
		map.on('load', () => render(modeSelect.value, Number(defaultYear)));
	}
}


let chatExpanded = false;
let currentLanguage = 'fr';

function translatePage(lang) {
	currentLanguage = lang;
	
	document.querySelectorAll('[data-fr]').forEach(el => {
		const text = el.getAttribute(`data-${lang}`);
		if (text) {
			if (el.tagName === 'INPUT') {
				el.placeholder = text;
			} else {
				el.textContent = text;
			}
		}
	});
	
	document.querySelectorAll('[data-fr-placeholder]').forEach(el => {
		const placeholder = el.getAttribute(`data-${lang}-placeholder`);
		if (placeholder) {
			el.placeholder = placeholder;
		}
	});
	
	document.querySelectorAll('.lang-btn').forEach(btn => {
		btn.classList.remove('active');
	});
	document.getElementById(`lang-${lang}`).classList.add('active');
}

function initLanguageSelector() {
	document.getElementById('lang-fr').addEventListener('click', () => translatePage('fr'));
	document.getElementById('lang-en').addEventListener('click', () => translatePage('en'));
}

function initAI() {
	const container = document.getElementById('ai-chat-container');
	const content = document.getElementById('ai-chat-content');
	const toggle = document.getElementById('ai-toggle');
	const input = document.getElementById('ai-chat-input');
	const sendBtn = document.getElementById('ai-send-btn');
	const messages = document.getElementById('ai-chat-messages');


	content.style.display = 'none';
	

	toggle.addEventListener('click', () => {
		chatExpanded = !chatExpanded;
		content.style.display = chatExpanded ? 'flex' : 'none';
		toggle.textContent = chatExpanded ? '✕' : '💬';
		
		if (chatExpanded && messages.children.length === 0) {
			const welcomeMsg = currentLanguage === 'fr' ? 
				'👋 Bonjour ! Je suis votre assistant IA spécialisé dans l\'immobilier français. Posez-moi des questions sur les données DVF !' :
				'👋 Hello! I am your AI assistant specialized in French real estate. Ask me questions about DVF data!';
			
			const examplesMsg = currentLanguage === 'fr' ? '💡 Exemples de questions:' : '💡 Example questions:';
			
			addMessage('assistant', welcomeMsg);
			addMessage('assistant', examplesMsg);
			
			const suggestionsDiv = document.createElement('div');
			suggestionsDiv.style.cssText = 'margin: 8px 0; display: flex; flex-direction: column; gap: 4px;';
			
			const suggestions = currentLanguage === 'fr' ? [
				"Quel arrondissement parisien a le plus progressé depuis 2020 ?",
				"Comment a évolué l'immobilier en France depuis 2021 ?",
				"Où investir dans Paris en 2024 ?",
				"🔮 Prédictions prix immobilier 2025 Paris",
				"🔮 Quels seront les prix en France en 2025 ?",
				"🔮 Arrondissements les plus chers en 2025"
			] : [
				"Which Paris district has progressed the most since 2020?",
				"How has real estate evolved in France since 2021?",
				"Where to invest in Paris in 2024?",
				"🔮 Real estate price predictions 2025 Paris",
				"🔮 What will prices be in France in 2025?",
				"🔮 Most expensive districts in 2025"
			];
			
			suggestions.forEach(suggestion => {
				const btn = document.createElement('button');
				btn.textContent = suggestion;
				btn.style.cssText = 'padding: 6px 10px; margin: 2px 0; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; text-align: left;';
				btn.onclick = () => {
					document.getElementById('ai-chat-input').value = suggestion;
					document.getElementById('ai-send-btn').click();
				};
				suggestionsDiv.appendChild(btn);
			});
			
			messages.appendChild(suggestionsDiv);
		}
	});


	function sendMessage() {
		const question = input.value.trim();
		if (!question) return;
		
		addMessage('user', question);
		input.value = '';
		sendBtn.disabled = true;
		
		const loadingMsg = addMessage('assistant', '', true);
		

		fetch('/api/ai/chat/', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({question, language: currentLanguage})
		})
		.then(res => res.json())
		.then(data => {
			loadingMsg.remove();
			
			if (data.error) {
				addMessage('assistant', `❌ Erreur: ${data.error}`);
			} else {
				addMessage('assistant', data.response);
				
	
				if (data.predictions) {
					displayPredictions(data.predictions);
				}
				

			}
		})
		.catch(err => {
			loadingMsg.remove();
			addMessage('assistant', '❌ Erreur de connexion. Vérifiez que le serveur fonctionne.');
			console.error('AI Error:', err);
		})
		.finally(() => {
			sendBtn.disabled = false;
		});
	}

	sendBtn.addEventListener('click', sendMessage);
	input.addEventListener('keypress', (e) => {
		if (e.key === 'Enter') sendMessage();
	});
}

function addMessage(type, content, isLoading = false) {
	const messages = document.getElementById('ai-chat-messages');
	const div = document.createElement('div');
	div.className = `ai-message ${type}`;
	
	if (isLoading) {
		div.className += ' ai-loading';
		div.textContent = currentLanguage === 'en' 
			? 'Analyzing data…'
			: 'Analyse en cours…';
	} else {
		div.innerHTML = content.replace(/\n/g, '<br>');
	}
	
	messages.appendChild(div);
	messages.scrollTop = messages.scrollHeight;
	return div;
}



function displayPredictions(predictions) {
	if (!predictions || !predictions.insights) return;
	

	const messages = document.getElementById('ai-chat-messages');
	const predDiv = document.createElement('div');
	predDiv.className = 'ai-message assistant prediction-message';
	predDiv.style.cssText = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-right: 10px; border-radius: 12px;';
	
	let predContent = '<strong>🔮 PRÉDICTIONS 2025</strong><br><br>';
	
	predictions.insights.forEach(insight => {
		predContent += `• ${insight}<br>`;
	});
	
	predDiv.innerHTML = predContent;
	messages.appendChild(predDiv);
	messages.scrollTop = messages.scrollHeight;
	
	
	if (predictions.top_arrondissements && predictions.top_arrondissements.length > 0) {
		const topDiv = document.createElement('div');
		topDiv.className = 'ai-message assistant';
		
		let topContent = '<strong>🏆 TOP 5 ARRONDISSEMENTS PRÉDITS 2025:</strong><br><br>';
		predictions.top_arrondissements.slice(0, 5).forEach((arr, index) => {
			const trend = arr.growth_percent > 0 ? '📈' : '📉';
			topContent += `${index + 1}. <strong>${arr.arrondissement}</strong><br>`;
			topContent += `   Prix prédit: ${arr.predicted_price_2025.toLocaleString('fr-FR')} €/m² ${trend} (${arr.growth_percent > 0 ? '+' : ''}${arr.growth_percent}%)<br><br>`;
		});
		
		topDiv.innerHTML = topContent;
		messages.appendChild(topDiv);
		messages.scrollTop = messages.scrollHeight;
	}
}


document.getElementById('start-app').addEventListener('click', () => {
	const welcomeScreen = document.getElementById('welcome-screen');
	welcomeScreen.classList.add('hidden');

	setTimeout(() => {
		welcomeScreen.style.display = 'none';
		
		initApp();
	}, 500);
});

initLanguageSelector();

function initApp() {

	if (map.isStyleLoaded()) {

		init().then(() => {
			setTimeout(initAI, 500);
		}).catch(console.error);
	} else {

		map.on('style.load', () => {
			init().then(() => {
				setTimeout(initAI, 500);
			}).catch(console.error);
		});
	}
} 