import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Zap, Droplets, Wind, Sun, Mountain, Database, Cpu, HardDrive, Thermometer } from 'lucide-react';

const PyramidDatacenterBlueprint = () => {
  const [activeLevel, setActiveLevel] = useState('overview');
  const [showSpecs, setShowSpecs] = useState(false);

  const levels = {
    'level-50': {
      name: 'Ebene -50m: Quantencore',
      icon: <Database className="w-6 h-6" />,
      color: 'from-blue-500 to-blue-700',
      components: [
        { name: 'Quantencomputer-Kern', temp: '<4K', power: '5 MW', cooling: 'Helium-Kryo' },
        { name: 'Grundwasser-Wärmetauscher', temp: '15°C', power: '-20 MW', cooling: 'Passiv' },
        { name: 'Energiespeicher (Schwungrad)', temp: '20°C', power: '50 MWh', cooling: 'Luftgekühlt' }
      ],
      description: 'Tiefste Ebene mit konstanter Erdtemperatur. Quantencomputer benötigen Kryokühlung unter 4 Kelvin.'
    },
    'level-20': {
      name: 'Ebene -20m: GPU-Cluster',
      icon: <Cpu className="w-6 h-6" />,
      color: 'from-purple-500 to-purple-700',
      components: [
        { name: 'GPU-Racks (10,000 Units)', temp: '65°C', power: '40 MW', cooling: 'Immersion (5 bar)' },
        { name: 'Kühlfluid-Tanks (Novec 7100)', temp: '90°C', power: '-', cooling: 'Druckkreislauf' },
        { name: 'Hot-Swap-Module', temp: '25°C', power: '0.5 MW', cooling: 'Luft' }
      ],
      description: 'Hauptrecheneinheiten in Hochdruck-Flüssigkeitskühlung. Siedepunkt bei 5 bar: 120°C.'
    },
    'level0': {
      name: 'Ebene 0-50m: Pyramiden-Kern',
      icon: <Mountain className="w-6 h-6" />,
      color: 'from-orange-500 to-orange-700',
      components: [
        { name: 'Zentraler Kaminschacht', temp: '40-80°C', power: 'Passiv', cooling: 'Thermischer Auftrieb' },
        { name: 'Ringförmige Server-Racks', temp: '50°C', power: '30 MW', cooling: 'Kamin-Zirkulation' },
        { name: 'RAM-Cluster (Petabyte-Scale)', temp: '45°C', power: '5 MW', cooling: 'Hybrid' },
        { name: 'Geopolymer-Wände (PCM-Einbettung)', temp: '20-30°C', power: '-', cooling: 'Thermische Masse' }
      ],
      description: 'Herzstück: Kamineffekt treibt passive Luftzirkulation. Geopolymer-Wände als thermischer Puffer.'
    },
    'level50': {
      name: 'Ebene 50-150m: Oberfläche',
      icon: <Sun className="w-6 h-6" />,
      color: 'from-yellow-500 to-yellow-700',
      components: [
        { name: 'Bifaziale Solarpanels', temp: '60°C', power: '+15 MW', cooling: 'Konvektion' },
        { name: 'Nachtkühlung (Abstrahlung)', temp: '-10°C', power: '-8 MW', cooling: 'Radiativ' },
        { name: 'Blitzableiter (Spitze)', temp: 'Ambient', power: '+0.1 MW', cooling: 'N/A' }
      ],
      description: 'Maximale Oberfläche für Solar-Harvest und nächtliche Wärmeabstrahlung. Pyramidengeometrie optimal.'
    }
  };

  const standortVergleich = [
    { name: 'Gizeh, Ägypten', solar: 2800, water: 'Nil-Aquifer', temp: '15-35°C', politics: '⚠️ UNESCO', score: 7 },
    { name: 'Atacama, Chile', solar: 3200, water: 'Pazifik (50km)', temp: '10-25°C', politics: '✅ Stabil', score: 9 },
    { name: 'Island', solar: 800, water: 'Geothermie', temp: '0-15°C', politics: '✅ Grün', score: 8 },
    { name: 'Namibia', solar: 3000, water: 'Grundwasser', temp: '15-30°C', politics: '✅ Offen', score: 8 },
    { name: 'Antarktis', solar: 1200, water: 'Eis/Schnee', temp: '-30°C', politics: '⚠️ Forschung', score: 6 }
  ];

  const materialSpecs = [
    { material: 'Geopolymer-Beton', use: 'Strukturwände', k: '1.4 W/mK', density: '2300 kg/m³', cost: '$200/m³' },
    { material: 'PCM (Phase Change Material)', use: 'Wärmepuffer', k: '0.2 W/mK', density: '880 kg/m³', cost: '$50/kg' },
    { material: 'Graphen-Nanotubes', use: 'Interne Leiter', k: '3000 W/mK', density: '2200 kg/m³', cost: '$500/m' },
    { material: '3M Novec 7100', use: 'Kühlfluid', k: '0.06 W/mK', density: '1520 kg/m³', cost: '$80/L' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-3">
            <Mountain className="w-10 h-10 text-orange-400" />
            Pyramiden-Exascale-Datacenter v2.0
          </h1>
          <p className="text-slate-300 text-lg">
            Hybrid-Architektur: Geminis Kamineffekt + Claudes Druckkühlung + Mistrals Modularität
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4 mb-6 justify-center flex-wrap">
          <button
            onClick={() => setActiveLevel('overview')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeLevel === 'overview' 
                ? 'bg-cyan-500 text-white' 
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Overview
          </button>
          {Object.keys(levels).map(key => (
            <button
              key={key}
              onClick={() => setActiveLevel(key)}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                activeLevel === key 
                  ? 'bg-purple-500 text-white' 
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {levels[key].name.split(':')[0]}
            </button>
          ))}
        </div>

        {/* Overview Section */}
        {activeLevel === 'overview' && (
          <div>
            <div className="bg-slate-800 rounded-lg p-6 mb-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Zap className="w-6 h-6 text-yellow-400" />
                Gesamtsystem-Übersicht
              </h2>
              
              {/* Pyramid Visual */}
              <div className="relative h-96 mb-6 flex items-end justify-center">
                {/* Base */}
                <div className="absolute bottom-0 w-full h-8 bg-gradient-to-r from-slate-700 to-slate-600 rounded"></div>
                
                {/* Underground levels */}
                <div className="absolute bottom-8 left-1/4 right-1/4 h-16 bg-gradient-to-b from-blue-600 to-blue-700 rounded-t opacity-80 flex items-center justify-center text-xs font-semibold">
                  -50m: Quantencore
                </div>
                <div className="absolute bottom-24 left-1/3 right-1/3 h-12 bg-gradient-to-b from-purple-600 to-purple-700 rounded-t opacity-80 flex items-center justify-center text-xs font-semibold">
                  -20m: GPU-Cluster
                </div>
                
                {/* Pyramid structure */}
                <svg className="absolute bottom-36 w-80 h-60" viewBox="0 0 200 150" preserveAspectRatio="xMidYMid meet">
                  {/* Main pyramid */}
                  <polygon 
                    points="100,10 20,150 180,150" 
                    fill="url(#pyramidGradient)" 
                    stroke="#f59e0b" 
                    strokeWidth="2"
                  />
                  {/* Center chimney */}
                  <line x1="100" y1="10" x2="100" y2="150" stroke="#ef4444" strokeWidth="3" strokeDasharray="5,5" />
                  {/* Solar panels */}
                  <rect x="25" y="75" width="70" height="5" fill="#fbbf24" opacity="0.8" />
                  <rect x="105" y="75" width="70" height="5" fill="#fbbf24" opacity="0.8" />
                  
                  <defs>
                    <linearGradient id="pyramidGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#f97316" />
                      <stop offset="100%" stopColor="#ea580c" />
                    </linearGradient>
                  </defs>
                </svg>
                
                {/* Labels */}
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 text-sm font-semibold text-yellow-400">
                  150m Spitze: Solar + Blitzableiter
                </div>
                <div className="absolute top-32 right-12 text-xs text-red-400 font-semibold">
                  Kaminschacht →
                </div>
              </div>

              {/* Key Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500/20 to-blue-700/20 rounded-lg p-4 border border-blue-500/30">
                  <div className="text-3xl font-bold text-blue-400">100 MW</div>
                  <div className="text-sm text-slate-300">Gesamtleistung</div>
                </div>
                <div className="bg-gradient-to-br from-green-500/20 to-green-700/20 rounded-lg p-4 border border-green-500/30">
                  <div className="text-3xl font-bold text-green-400">PUE 1.08</div>
                  <div className="text-sm text-slate-300">Effizienz</div>
                </div>
                <div className="bg-gradient-to-br from-purple-500/20 to-purple-700/20 rounded-lg p-4 border border-purple-500/30">
                  <div className="text-3xl font-bold text-purple-400">50 Jahre</div>
                  <div className="text-sm text-slate-300">Thermische Trägheit</div>
                </div>
                <div className="bg-gradient-to-br from-orange-500/20 to-orange-700/20 rounded-lg p-4 border border-orange-500/30">
                  <div className="text-3xl font-bold text-orange-400">152k m²</div>
                  <div className="text-sm text-slate-300">Solar-Fläche</div>
                </div>
              </div>
            </div>

            {/* Standort-Vergleich */}
            <div className="bg-slate-800 rounded-lg p-6 mb-6">
              <h2 className="text-2xl font-bold mb-4">Standort-Vergleich (Optimiert)</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left p-3">Standort</th>
                      <th className="text-center p-3">Solar (kWh/m²/Jahr)</th>
                      <th className="text-center p-3">Kühlung</th>
                      <th className="text-center p-3">Temp-Range</th>
                      <th className="text-center p-3">Politik</th>
                      <th className="text-center p-3">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {standortVergleich.map((standort, idx) => (
                      <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                        <td className="p-3 font-semibold">{standort.name}</td>
                        <td className="p-3 text-center">{standort.solar}</td>
                        <td className="p-3 text-center text-cyan-400">{standort.water}</td>
                        <td className="p-3 text-center">{standort.temp}</td>
                        <td className="p-3 text-center">{standort.politics}</td>
                        <td className="p-3 text-center">
                          <span className={`px-3 py-1 rounded font-bold ${
                            standort.score >= 8 ? 'bg-green-500 text-white' : 
                            standort.score >= 7 ? 'bg-yellow-500 text-black' : 
                            'bg-red-500 text-white'
                          }`}>
                            {standort.score}/10
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-4 text-sm text-slate-400">
                <strong>Empfehlung:</strong> Atacama oder Namibia für maximale Solar-Effizienz + politische Stabilität.
              </p>
            </div>
          </div>
        )}

        {/* Level Detail View */}
        {activeLevel !== 'overview' && levels[activeLevel] && (
          <div className="bg-slate-800 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-4 mb-6">
              <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${levels[activeLevel].color} flex items-center justify-center`}>
                {levels[activeLevel].icon}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{levels[activeLevel].name}</h2>
                <p className="text-slate-400">{levels[activeLevel].description}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {levels[activeLevel].components.map((comp, idx) => (
                <div key={idx} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                  <h3 className="font-semibold text-lg mb-2">{comp.name}</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Temperatur:</span>
                      <span className="text-cyan-400">{comp.temp}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Leistung:</span>
                      <span className="text-orange-400">{comp.power}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Kühlung:</span>
                      <span className="text-green-400">{comp.cooling}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Material Specs */}
        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Material-Spezifikationen</h2>
            <button
              onClick={() => setShowSpecs(!showSpecs)}
              className="text-cyan-400 hover:text-cyan-300 flex items-center gap-2"
            >
              {showSpecs ? <ChevronUp /> : <ChevronDown />}
              {showSpecs ? 'Verbergen' : 'Details anzeigen'}
            </button>
          </div>

          {showSpecs && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left p-3">Material</th>
                    <th className="text-left p-3">Verwendung</th>
                    <th className="text-center p-3">Wärmeleitfähigkeit</th>
                    <th className="text-center p-3">Dichte</th>
                    <th className="text-center p-3">Kosten</th>
                  </tr>
                </thead>
                <tbody>
                  {materialSpecs.map((mat, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50">
                      <td className="p-3 font-semibold text-purple-400">{mat.material}</td>
                      <td className="p-3">{mat.use}</td>
                      <td className="p-3 text-center text-cyan-400">{mat.k}</td>
                      <td className="p-3 text-center">{mat.density}</td>
                      <td className="p-3 text-center text-orange-400">{mat.cost}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Next Steps */}
        <div className="mt-6 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg p-6 border border-cyan-500/30">
          <h3 className="text-xl font-bold mb-3">Nächste Schritte:</h3>
          <ol className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">1.</span>
              <span><strong>CAD-Modell:</strong> Detaillierte 3D-Zeichnung mit Autodesk Fusion 360</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">2.</span>
              <span><strong>Thermische Simulation:</strong> ANSYS Fluent für Wärmefluss-Analyse</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">3.</span>
              <span><strong>Kosten-Nutzen-Analyse:</strong> 30-Jahres-Projektion (CAPEX vs. OPEX)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-400 font-bold">4.</span>
              <span><strong>Prototyp-Test:</strong> 1:100 Modell in Island/Atacama</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default PyramidDatacenterBlueprint;