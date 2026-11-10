export type CaseId = 'adaptive-game-soundtracks' | 'co-located-vr' | 'work-storage-caching';
type Metric = { value: string; key: string; noteKey: string };
type FlowStep = { key: string; detailKey: string };
type ChartView = { key: string; unit: string; max: number; rows: { label: string; value: number }[] };
export interface AcademicCase {
  id: CaseId;
  authorNames: string[];
  source: string;
  metrics: Metric[];
  flow: FlowStep[];
  charts: ChartView[];
}
export const academicCases: Record<CaseId, AcademicCase> = {
  'adaptive-game-soundtracks': {
    id: 'adaptive-game-soundtracks',
    authorNames: ['Jon Friis Jakobsen','Mia Helmin Kongstad Welling','Emil Storm Eriksen'],
    source: 'Generative Adaptive Soundtracks for Video Games, sections III–VIII, tables IV–V',
    metrics: [
      { value: '30–43 ms', key: 'metric1', noteKey: 'metric1note' },
      { value: '10.8–15.7×', key: 'metric2', noteKey: 'metric2note' },
      { value: '6.0–8.8 s', key: 'metric3', noteKey: 'metric3note' }
    ],
    flow: ['state','parameters','websocket','inference','delivery'].map(key => ({key,detailKey:key+'Detail'})),
    charts: [
      { key:'firstEvent', unit:'ms',max:700,rows:[
        {label:'CUDA Medium',value:30},{label:'CUDA Large',value:43},{label:'CPU Medium',value:298},{label:'CPU Large',value:631}
      ]},
      { key:'completion',unit:'ms',max:150000,rows:[
        {label:'CUDA Medium',value:6029},{label:'CUDA Large',value:8755},{label:'CPU Medium',value:65320},{label:'CPU Large',value:137327}
      ]}
    ]
  },
  'co-located-vr': {
    id: 'co-located-vr',
    authorNames: ['Jon F. Jakobsen','Kasper V. Nielsen','Sebastian M. H. Jensen','Sebastian P. H. Pedersen'],
    source: 'Co-located Multi-user VR System — We Are Headset, sections IV–VI, tables I–III',
    metrics: [
      {value:'85.1 min',key:'metric1',noteKey:'metric1note'},
      {value:'58.2 ms',key:'metric2',noteKey:'metric2note'},
      {value:'1.21 mm',key:'metric3',noteKey:'metric3note'}
    ],
    flow: ['host','discover','align','synchronize','measure'].map(key => ({key,detailKey:key+'Detail'})),
    charts: [
      {key:'network',unit:'ms',max:100,rows:[
        {label:'Mean RTT',value:58.2},{label:'P95 RTT',value:86},{label:'Reference target',value:75}
      ]},
      {key:'alignment',unit:'mm',max:10,rows:[
        {label:'Mean error',value:1.21},{label:'Max error',value:5.78},{label:'Reference threshold',value:10}
      ]}
    ]
  },
  'work-storage-caching': {
    id:'work-storage-caching',
    authorNames:['Jon Friis Jakobsen','Mads Würtz Pedersen','Michael Ringhus Gertz'],
    source:'Work-Storage Balancing through Caching, sections IV–IX, tables I–II',
    metrics:[
      {value:'94.53%',key:'metric1',noteKey:'metric1note'},
      {value:'6',key:'metric2',noteKey:'metric2note'},
      {value:'1 / 2 / 5',key:'metric3',noteKey:'metric3note'}
    ],
    flow:['request','lookup','hit','miss','record'].map(key=>({key,detailKey:key+'Detail'})),
    charts:[
      {key:'hit1',unit:'%',max:100,rows:[
        {label:'A2C',value:18.19},{label:'DQN',value:36.15},{label:'LFU',value:89.16},{label:'LRU',value:56.89},{label:'PPO',value:22.54},{label:'TTL',value:94.53}
      ]},
      {key:'hit5',unit:'%',max:100,rows:[
        {label:'A2C',value:5.40},{label:'DQN',value:11.78},{label:'LFU',value:22.78},{label:'LRU',value:21.51},{label:'PPO',value:8.79},{label:'TTL',value:22.84}
      ]},
      {key:'miss1',unit:'ms',max:200,rows:[
        {label:'A2C',value:111.13},{label:'DQN',value:147.71},{label:'LFU',value:44.19},{label:'LRU',value:166.05},{label:'PPO',value:66.00},{label:'TTL',value:80.88}
      ]}
    ]
  }
};
export function isAcademicCase(id: string): id is CaseId { return Object.hasOwn(academicCases,id); }
