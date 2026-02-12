export interface Publication {
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  venueType: 'conference' | 'journal' | 'workshop' | 'preprint' | 'thesis' | 'other';
  doi?: string;
  url?: string;
  pdf?: string;
  code?: string;
  video?: string;
  slides?: string;
  abstract?: string;
  selected?: boolean;
  preview?: string;
  bibtexType: string;
}

export interface NewsItem {
  title: string;
  date: Date;
  content: string;
  pinned?: boolean;
}

export interface Project {
  title: string;
  description: string;
  category: string;
  tags: string[];
  image?: string;
  url?: string;
  github?: string;
  featured?: boolean;
  date: Date;
}

export interface Course {
  course_id: string;
  title: string;
  semester: string;
  year: number;
  role: string;
  university: string;
  description?: string;
  url?: string;
}

export interface CVEducation { degree: string; institution: string; year: string; description?: string; }
export interface CVExperience { title: string; organization: string; start_date: string; end_date: string; description?: string; }
export interface CVData {
  education: CVEducation[];
  experience: CVExperience[];
  skills: { category: string; items: string[] }[];
  awards: { title: string; organization: string; year: number }[];
  service: { role: string; organization: string; years: string }[];
}

export interface TeamMember { name: string; role: string; image?: string; url?: string; email?: string; alumni?: boolean; year_left?: number; }
export interface Talk { title: string; event: string; date: Date; location?: string; slides?: string; video?: string; url?: string; }
export interface BookEntry { title: string; author: string; cover?: string; rating?: number; notes?: string; url?: string; date_read?: Date; }
export interface BlogPost { title: string; slug: string; date: Date; tags: string[]; description: string; readingTime: number; draft?: boolean; }
