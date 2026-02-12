import type { Publication } from './types';

export function parseBibTeX(bibtex: string): Publication[] {
  const entries: Publication[] = [];
  const entryRegex = /@(\w+)\s*\{\s*([^,]*?)\s*,([\s\S]*?)(?=\n\s*@|\s*$)/g;
  let match: RegExpExecArray | null;

  while ((match = entryRegex.exec(bibtex)) !== null) {
    const bibtexType = match[1].toLowerCase();
    const id = match[2].trim();
    const body = match[3];
    if (['comment', 'preamble', 'string'].includes(bibtexType)) continue;

    const fields = parseFields(body);
    const authors = parseAuthors(fields.author || '');
    const year = parseInt(fields.year || '0', 10);
    const venue = fields.journal || fields.booktitle || fields.school || fields.institution || '';

    const venueLower = venue.toLowerCase();
    let venueType: Publication['venueType'] = 'other';
    if (venueLower.includes('workshop')) venueType = 'workshop';
    else if (venueLower.includes('arxiv') || venueLower.includes('preprint')) venueType = 'preprint';
    else if (bibtexType === 'inproceedings' || bibtexType === 'conference') venueType = 'conference';
    else if (bibtexType === 'article') {
      // Detect conference proceedings published as @article (e.g., IROS, ICRA)
      const confKeywords = /\b(conference|proceedings|IROS|ICRA|CVPR|ICCV|ECCV|NeurIPS|ICML|ICLR|AAAI|IJCAI|ACL|EMNLP|NAACL|SIGIR|KDD|WWW|CHI|HRI|RSS|CoRL)\b/i;
      venueType = confKeywords.test(venue) ? 'conference' : 'journal';
    }
    else if (bibtexType === 'misc' || bibtexType === 'unpublished') venueType = 'preprint';
    else if (bibtexType === 'phdthesis' || bibtexType === 'mastersthesis') venueType = 'thesis';

    entries.push({
      id, title: cleanTeX(fields.title || ''), authors, year, venue: cleanTeX(venue), venueType,
      doi: fields.doi, url: fields.url, pdf: fields.pdf, code: fields.code,
      video: fields.video, slides: fields.slides,
      abstract: fields.abstract ? cleanTeX(fields.abstract) : undefined,
      selected: fields.selected === 'true' || fields.selected === 'yes',
      preview: fields.preview || undefined,
      bibtexType,
    });
  }
  return entries.sort((a, b) => b.year - a.year);
}

function parseFields(body: string): Record<string, string> {
  const fields: Record<string, string> = {};
  const re = /(\w+)\s*=\s*/g;
  let m: RegExpExecArray | null;

  while ((m = re.exec(body)) !== null) {
    const key = m[1].toLowerCase();
    let i = re.lastIndex;
    // skip whitespace
    while (i < body.length && /\s/.test(body[i])) i++;
    if (i >= body.length) break;

    let value = '';
    const ch = body[i];
    if (ch === '{') {
      // Brace-delimited: count depth
      let depth = 0;
      const start = i;
      for (; i < body.length; i++) {
        if (body[i] === '{') depth++;
        else if (body[i] === '}') { depth--; if (depth === 0) { i++; break; } }
      }
      value = body.slice(start + 1, i - 1);
    } else if (ch === '"') {
      // Quote-delimited
      i++; // skip opening quote
      const start = i;
      while (i < body.length && body[i] !== '"') i++;
      value = body.slice(start, i);
      i++; // skip closing quote
    } else if (/\d/.test(ch)) {
      // Bare number
      const start = i;
      while (i < body.length && /\d/.test(body[i])) i++;
      value = body.slice(start, i);
    }
    fields[key] = value.trim();
    re.lastIndex = i;
  }
  return fields;
}

function parseAuthors(authorStr: string): string[] {
  if (!authorStr) return [];
  return authorStr.split(/\s+and\s+/i).map(a => {
    const parts = a.trim().split(/\s*,\s*/);
    return parts.length === 2 ? `${parts[1].trim()} ${parts[0].trim()}` : a.trim();
  }).filter(a => a.length > 0);
}

function cleanTeX(str: string): string {
  return str
    .replace(/\\[`'^"~H.cv]\{([a-zA-Z])\}/g, '$1')  // \'{e} -> e, etc.
    .replace(/\\[`'^"~H.cv]([a-zA-Z])/g, '$1')        // \'e -> e
    .replace(/\{\\([a-zA-Z])\}/g, '$1')                // {\i} -> i, {\o} -> o
    .replace(/\\(ss|ae|oe|AE|OE|aa|AA|o|O|i|l|L)\b/g, (_, c) => {
      const map: Record<string, string> = { ss: '\u00DF', ae: '\u00E6', oe: '\u0153', AE: '\u00C6', OE: '\u0152', aa: '\u00E5', AA: '\u00C5', o: '\u00F8', O: '\u00D8', i: 'i', l: '\u0142', L: '\u0141' };
      return map[c] || c;
    })
    .replace(/[{}]/g, '')
    .replace(/\\textbf|\\textit|\\emph/g, '')
    .replace(/~/g, ' ')
    .replace(/\\\\/g, '')
    .replace(/\\&/g, '&')
    .trim();
}

export function getPublicationsByYear(pubs: Publication[]): Map<number, Publication[]> {
  const byYear = new Map<number, Publication[]>();
  for (const pub of pubs) {
    if (!byYear.has(pub.year)) byYear.set(pub.year, []);
    byYear.get(pub.year)!.push(pub);
  }
  return new Map([...byYear.entries()].sort(([a], [b]) => b - a));
}
