<!DOCTYPE html>
<html lang="nl" class="h-full bg-slate-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MPG Dashboard & MKI Connector</title>
    <!-- Tailwind CSS for modern responsive design -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome for beautiful environmental & UI icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="h-full flex flex-col text-slate-800">

    <header class="bg-emerald-900 text-white shadow-md">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-emerald-700 rounded-lg text-emerald-100">
                    <i class="fa-solid fa-leaf text-2xl animate-pulse"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">MPG & MKI Verwerker</h1>
                    <p class="text-xs text-emerald-300">Dynamo-naar-Web Milieuprestatie Dashboard</p>
                </div>
            </div>
            <div class="flex items-center gap-2 text-xs bg-emerald-800 px-3 py-1.5 rounded-full text-emerald-100 border border-emerald-700">
                <span class="w-2 h-2 bg-emerald-400 rounded-full inline-block"></span>
                <span>Externe Interface Actief</span>
            </div>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 overflow-y-auto">
        
        <!-- Left Panel: Input, Upload & Parameters -->
        <div class="lg:col-span-4 flex flex-col gap-6">
            
            <!-- STEP 1: Paste Dynamo Output -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-md font-semibold text-slate-900 flex items-center gap-2">
                        <span class="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">1</span>
                        Revit Data Uploaden
                    </h2>
                    <span class="text-xs text-slate-400">JSON Bestand</span>
                </div>
                
                <div class="flex flex-col items-center justify-center w-full">
                    <label for="jsonFileInput" class="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-xl cursor-pointer bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 transition-all group">
                        <div class="flex flex-col items-center justify-center pt-5 pb-6">
                            <i class="fa-solid fa-file-arrow-up text-3xl text-slate-400 group-hover:text-emerald-500 mb-3 transition-colors"></i>
                            <p class="mb-1 text-sm text-slate-600 font-medium">Klik om JSON te kiezen</p>
                            <p class="text-xs text-slate-500" id="fileNameDisplay">Selecteer revit_mki_export.json</p>
                        </div>
                        <input id="jsonFileInput" type="file" accept=".json" class="hidden" onchange="handleFileUpload(event)" />
                    </label>
                </div>
            </div>

            <!-- STEP 2: Project Specifications -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h2 class="text-md font-semibold text-slate-900 flex items-center gap-2 mb-4">
                    <span class="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">2</span>
                    Project Parameters
                </h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-500 mb-1">Gebouwfunctie</label>
                        <select id="buildingFunction" class="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 outline-none focus:ring-2 focus:ring-emerald-500">
                            <option value="residential">Woonfunctie (Eengezins / Appartement)</option>
                            <option value="office">Kantoorfunctie</option>
                            <option value="education">Bijeenkomst / Onderwijs</option>
                            <option value="health">Gezondheidszorg</option>
                        </select>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-500 mb-1">BVO (m²)</label>
                            <input type="number" id="bvoInput" value="120" min="1" class="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 outline-none focus:ring-2 focus:ring-emerald-500">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-500 mb-1">Levensduur (jaar)</label>
                            <input type="number" id="lifespanInput" value="75" min="1" class="w-full text-sm bg-slate-50 border border-slate-200 rounded-xl p-2.5 outline-none focus:ring-2 focus:ring-emerald-500">
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- Right Panel: Materials Table & Live MPG Calculations -->
        <div class="lg:col-span-8 flex flex-col gap-6">
            
            <!-- Live Scoreboard KPI Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">MPG Score</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <span id="mpgValue" class="text-3xl font-bold text-emerald-600">0.00</span>
                        <span class="text-xs text-slate-500 font-medium">€ / m² BVO·jr</span>
                    </div>
                    <div class="mt-2 text-xs flex items-center gap-1.5" id="mpgStatus">
                        <span class="w-2.5 h-2.5 rounded-full bg-slate-300"></span>
                        <span class="text-slate-500">Geen data ingeladen</span>
                    </div>
                </div>
                
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Totale Schaduwkosten</span>
                    <div class="flex items-baseline gap-1 mt-2">
                        <span class="text-xl font-semibold text-slate-500">€</span>
                        <span id="totalMkiValue" class="text-3xl font-bold text-slate-800">0.00</span>
                    </div>
                    <span class="text-xs text-slate-400 mt-2">MKI som over de gehele levensduur</span>
                </div>

                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Materialen in Model</span>
                    <div class="flex items-baseline gap-2 mt-2">
                        <span id="materialsCount" class="text-3xl font-bold text-slate-800">0</span>
                        <span class="text-xs text-slate-500 font-medium">unieke typen</span>
                    </div>
                    <span class="text-xs text-emerald-600 mt-2 font-medium" id="mappedCount">0 van de 0 gemapped</span>
                </div>
            </div>

            <!-- Material Mapper Workspace -->
            <div class="bg-white rounded-2xl shadow-sm border border-slate-100 flex-1 flex flex-col overflow-hidden min-h-[400px]">
                <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <h3 class="text-lg font-bold text-slate-900">Materialen Mappen & MKI Koppelen</h3>
                        <p class="text-xs text-slate-500">Verbind je Revit-materialen aan NMD milieugemiddeldes op de achtergrond</p>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="aiMapMaterials()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium px-3.5 py-2 rounded-xl shadow-sm transition-all flex items-center gap-2">
                            <i class="fa-solid fa-cloud-arrow-down"></i>
                            Koppel NMD Gemiddeldes
                        </button>
                    </div>
                </div>

                <div class="overflow-x-auto flex-1">
                    <table class="min-w-full divide-y divide-slate-100">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Revit Materiaal</th>
                                <th class="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Hoeveelheid (m³ / m²)</th>
                                <th class="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">NMD Categorie / Match</th>
                                <th class="px-6 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">MKI Score (€)</th>
                                <th class="px-6 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Totale Milieulast</th>
                            </tr>
                        </thead>
                        <tbody id="materialsTableBody" class="bg-white divide-y divide-slate-100 text-sm">
                            <!-- Dynamic Content Loaded Here -->
                            <tr>
                                <td colspan="5" class="px-6 py-12 text-center text-slate-400">
                                    <div class="flex flex-col items-center gap-2">
                                        <i class="fa-solid fa-arrow-left-long text-3xl text-slate-300 mb-2"></i>
                                        <p class="font-medium text-slate-500">Geen Revit modelgegevens actief</p>
                                        <p class="text-xs">Upload het JSON-bestand uit Dynamo in stap 1 om te beginnen.</p>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </main>

    <!-- Custom Toast Notification Box -->
    <div id="toastBox" class="fixed bottom-5 right-5 z-50 transform translate-y-20 opacity-0 transition-all duration-300 bg-slate-900 text-white px-5 py-3.5 rounded-2xl shadow-2xl flex items-center gap-3 text-sm">
        <span id="toastIcon"><i class="fa-solid fa-circle-info text-emerald-400"></i></span>
        <span id="toastMessage">Actie succesvol uitgevoerd</span>
    </div>

    <script>
        // Default Mock MKI Database (NL NMD Estimates)
        const mockMkiDatabase = [
            { id: "beton", label: "Constructiebeton (C30/37)", mki_m3: 15.50, mki_m2: null, unit: "m³" },
            { id: "baksteen", label: "Metselwerk baksteen gevel", mki_m3: 45.00, mki_m2: null, unit: "m³" },
            { id: "glas", label: "Isolerend HR++ glas (dubbel)", mki_m3: null, mki_m2: 6.20, unit: "m²" },
            { id: "hout_kozijn", label: "Hout (Naaldhout / Lariks)", mki_m3: -25.00, mki_m2: null, unit: "m³" }, // Carbon capture negative MKI
            { id: "gips", label: "Gipsplaten (binnenwanden)", mki_m3: null, mki_m2: 1.80, unit: "m²" },
            { id: "isolatie_minerale_wol", label: "Minerale wol isolatiedeken", mki_m3: 12.00, mki_m2: null, unit: "m³" },
            { id: "cement", label: "Dekvloer zandcement", mki_m3: 18.20, mki_m2: null, unit: "m³" },
            { id: "staal", label: "Staalconstructieprofielen S235", mki_m3: 145.00, mki_m2: null, unit: "m³" }
        ];

        let projectData = {
            project_info: { document_title: "Nieuw Project", estimated_bvo: 120 },
            materials: []
        };

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Update UI to show selected file
            const display = document.getElementById('fileNameDisplay');
            display.innerText = "Bestand: " + file.name;
            display.classList.add('text-emerald-600', 'font-semibold');

            const reader = new FileReader();
            reader.onload = function(e) {
                const jsonText = e.target.result;
                processRevitData(jsonText);
            };
            reader.readAsText(file);
        }

        function processRevitData(jsonText) {
            if (!jsonText) {
                showToast("Bestand is leeg!", "warning");
                return;
            }

            try {
                const parsed = JSON.parse(jsonText);
                if (!parsed.materials || !Array.isArray(parsed.materials)) {
                    throw new Error("De JSON mist de 'materials' array.");
                }

                projectData = parsed;
                
                // Update Project parameters from JSON if available
                if (parsed.project_info) {
                    if (parsed.project_info.estimated_bvo) {
                        document.getElementById('bvoInput').value = parsed.project_info.estimated_bvo;
                    }
                }

                showToast("Revit model succesvol ingeladen!", "success");
                renderMaterialsTable();
                calculateMpg();

            } catch (err) {
                showToast("Ongeldige JSON format: " + err.message, "error");
            }
        }

        function renderMaterialsTable() {
            const tbody = document.getElementById('materialsTableBody');
            tbody.innerHTML = '';

            if (projectData.materials.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-slate-400">Geen materialen gevonden.</td></tr>`;
                return;
            }

            document.getElementById('materialsCount').innerText = projectData.materials.length;

            projectData.materials.forEach((mat, idx) => {
                // Try to find a best matched category automatically on load
                if (!mat.mapped_db_id) {
                    const matched = autoMatchMaterial(mat.name);
                    mat.mapped_db_id = matched ? matched.id : "";
                    mat.use_unit = matched ? matched.unit : "m³";
                    mat.mki_factor = matched ? (matched.unit === "m³" ? matched.mki_m3 : matched.mki_m2) : 0;
                }

                const optionsHtml = mockMkiDatabase.map(dbItem => {
                    const isSelected = dbItem.id === mat.mapped_db_id ? 'selected' : '';
                    return `<option value="${dbItem.id}" ${isSelected}>${dbItem.label} (${dbItem.unit})</option>`;
                }).join('');

                const qtyVal = mat.use_unit === "m²" ? mat.area_m2 : mat.volume_m3;
                const totalMki = (qtyVal * (mat.mki_factor || 0)).toFixed(2);

                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50/50 transition-colors";
                tr.innerHTML = `
                    <td class="px-6 py-4 font-medium text-slate-900">
                        ${mat.name}
                    </td>
                    <td class="px-6 py-4 text-slate-500 text-xs">
                        <div class="flex flex-col gap-0.5">
                            <span class="${mat.use_unit === 'm³' ? 'font-semibold text-slate-700' : ''}">Vol: ${mat.volume_m3.toFixed(2)} m³</span>
                            <span class="${mat.use_unit === 'm²' ? 'font-semibold text-slate-700' : ''}">Opp: ${mat.area_m2.toFixed(2)} m²</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <select onchange="updateMapping(${idx}, this.value)" class="bg-white border border-slate-200 rounded-lg p-1.5 text-xs outline-none focus:ring-2 focus:ring-emerald-500 max-w-xs">
                            <option value="">-- Kies categorie --</option>
                            ${optionsHtml}
                        </select>
                    </td>
                    <td class="px-6 py-4 text-slate-600 font-mono text-xs">
                        € ${(mat.mki_factor || 0).toFixed(2)} / ${mat.use_unit}
                    </td>
                    <td class="px-6 py-4 text-right font-semibold text-slate-900 font-mono text-xs">
                        € ${totalMki}
                    </td>
                `;
                tbody.appendChild(tr);
            });

            updateMappedCounter();
        }

        function autoMatchMaterial(name) {
            const lower = name.toLowerCase();
            if (lower.includes('beton') || lower.includes('concrete')) return mockMkiDatabase.find(d => d.id === 'beton');
            if (lower.includes('glas') || lower.includes('glass') || lower.includes('glazing')) return mockMkiDatabase.find(d => d.id === 'glas');
            if (lower.includes('hout') || lower.includes('wood') || lower.includes('timber') || lower.includes('kozijn')) return mockMkiDatabase.find(d => d.id === 'hout_kozijn');
            if (lower.includes('gips') || lower.includes('drywall') || lower.includes('plaster')) return mockMkiDatabase.find(d => d.id === 'gips');
            if (lower.includes('isolatie') || lower.includes('wool') || lower.includes('isol')) return mockMkiDatabase.find(d => d.id === 'isolatie_minerale_wol');
            if (lower.includes('cement') || lower.includes('dekvloer')) return mockMkiDatabase.find(d => d.id === 'cement');
            if (lower.includes('staal') || lower.includes('steel') || lower.includes('structure')) return mockMkiDatabase.find(d => d.id === 'staal');
            if (lower.includes('brick') || lower.includes('steen') || lower.includes('metsel')) return mockMkiDatabase.find(d => d.id === 'baksteen');
            return null;
        }

        function updateMapping(index, dbId) {
            const mat = projectData.materials[index];
            if (!dbId) {
                mat.mapped_db_id = "";
                mat.mki_factor = 0;
            } else {
                const dbItem = mockMkiDatabase.find(d => d.id === dbId);
                mat.mapped_db_id = dbId;
                mat.use_unit = dbItem.unit;
                mat.mki_factor = dbItem.unit === "m³" ? dbItem.mki_m3 : dbItem.mki_m2;
            }
            renderMaterialsTable();
            calculateMpg();
        }

        function updateMappedCounter() {
            const mapped = projectData.materials.filter(m => m.mapped_db_id).length;
            const total = projectData.materials.length;
            document.getElementById('mappedCount').innerText = `${mapped} van de ${total} gekoppeld`;
        }

        function calculateMpg() {
            const bvo = parseFloat(document.getElementById('bvoInput').value) || 1;
            const lifespan = parseFloat(document.getElementById('lifespanInput').value) || 1;
            
            let grandTotalMki = 0.0;

            projectData.materials.forEach(mat => {
                if (mat.mapped_db_id) {
                    const qty = mat.use_unit === "m²" ? mat.area_m2 : mat.volume_m3;
                    grandTotalMki += (qty * mat.mki_factor);
                }
            });

            // MPG Formula: Sum MKI / (BVO * Lifespan)
            const mpg = grandTotalMki / (bvo * lifespan);

            document.getElementById('totalMkiValue').innerText = grandTotalMki.toLocaleString('nl-NL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            
            const mpgEl = document.getElementById('mpgValue');
            mpgEl.innerText = mpg.toFixed(3);

            // Update MPG Status Indicators according to NL Building Guidelines (Standard target: < 0.8)
            const statusEl = document.getElementById('mpgStatus');
            if (grandTotalMki === 0) {
                statusEl.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-slate-300"></span><span class="text-slate-500 text-xs">Geen actieve mapping</span>`;
            } else if (mpg <= 0.5) {
                statusEl.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span class="text-emerald-700 text-xs font-semibold">Uitstekend (BENG compliant)</span>`;
            } else if (mpg <= 0.8) {
                statusEl.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span><span class="text-amber-700 text-xs font-semibold">Voldoet aan bouwbesluit</span>`;
            } else {
                statusEl.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span><span class="text-rose-700 text-xs font-semibold">Te hoog (Aandacht vereist!)</span>`;
            }
        }

        async function aiMapMaterials() {
            if (projectData.materials.length === 0) {
                showToast("Laad eerst Revit materialen in!", "warning");
                return;
            }

            showToast("NMD gemiddeldes ophalen en mappen in achtergrond...", "info");

            // Extract material list
            const matNames = projectData.materials.map(m => m.name);
            
            const systemPrompt = "Je bent een expert in de Nederlandse Milieuprestatie Gebouwen (MPG) en de Nationale Milieudatabase (NMD). Je taak is om Revit materiaalnamen te matchen met de meest geschikte NMD categorieën uit deze lijst: " + JSON.stringify(mockMkiDatabase.map(d => ({id: d.id, label: d.label})));
            const userQuery = `Geef voor elk van de volgende Revit-materialen de meest geschikte ID terug uit de lijst. Antwoord in een valide JSON-lijst met objecten met keys 'material_name' en 'matched_id'. De materialen zijn: ${JSON.stringify(matNames)}`;

            try {
                // Call Gemini using Canvas system fetch instructions
                const apiKey = ""; // Canvas handles injecting keys automatically
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=${apiKey}`;

                const payload = {
                    contents: [{ parts: [{ text: userQuery }] }],
                    generationConfig: {
                        responseMimeType: "application/json",
                        responseSchema: {
                            type: "ARRAY",
                            items: {
                                type: "OBJECT",
                                properties: {
                                    material_name: { type: "STRING" },
                                    matched_id: { type: "STRING" }
                                },
                                required: ["material_name", "matched_id"]
                            }
                        }
                    },
                    systemInstruction: {
                        parts: [{ text: systemPrompt }]
                    }
                };

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                const jsonText = result.candidates?.[0]?.content?.parts?.[0]?.text;
                const matches = JSON.parse(jsonText);

                // Apply AI mappings
                matches.forEach(match => {
                    const localMat = projectData.materials.find(m => m.name === match.material_name);
                    if (localMat && match.matched_id) {
                        const dbItem = mockMkiDatabase.find(d => d.id === match.matched_id);
                        if (dbItem) {
                            localMat.mapped_db_id = dbItem.id;
                            localMat.use_unit = dbItem.unit;
                            localMat.mki_factor = dbItem.unit === "m³" ? dbItem.mki_m3 : dbItem.mki_m2;
                        }
                    }
                });

                renderMaterialsTable();
                calculateMpg();
                showToast("NMD Gemiddeldes succesvol gekoppeld!", "success");

            } catch (err) {
                console.error("Gemini mapping failed", err);
                showToast("NMD-koppeling mislukt, we gebruiken de standaard matchers.", "warning");
            }
        }

        function showToast(message, type = "success") {
            const toast = document.getElementById('toastBox');
            const icon = document.getElementById('toastIcon');
            const msg = document.getElementById('toastMessage');

            msg.innerText = message;
            
            if (type === "success") {
                icon.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400 text-lg"></i>`;
            } else if (type === "warning") {
                icon.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-400 text-lg"></i>`;
            } else if (type === "error") {
                icon.innerHTML = `<i class="fa-solid fa-circle-xmark text-rose-500 text-lg"></i>`;
            } else {
                icon.innerHTML = `<i class="fa-solid fa-circle-info text-blue-400 text-lg"></i>`;
            }

            toast.classList.remove('translate-y-20', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');

            setTimeout(() => {
                toast.classList.remove('translate-y-0', 'opacity-100');
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 4000);
        }

        // Watchers to recalculate values when project inputs change
        document.getElementById('bvoInput').addEventListener('input', calculateMpg);
        document.getElementById('lifespanInput').addEventListener('input', calculateMpg);
        document.getElementById('buildingFunction').addEventListener('change', calculateMpg);

    </script>
</body>
</html>
