import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ALL_TOOLS, SearchableTool } from '../../../app_data/all-tools.data';
import { TOOLS_CATEGORIES } from '../../../app_data/tools-category.data';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
})
export class HomeComponent {
  searchQuery: string = '';
  searchResults: SearchableTool[] = [];
  isSearching: boolean = false;
  
  // Grouped tools for the comprehensive list
  categoriesWithTools: { name: string, icon: string, count: number, tools: SearchableTool[] }[] = [];

  constructor() {
    this.groupTools();
  }

  groupTools() {
    const groups = new Map<string, SearchableTool[]>();
    
    ALL_TOOLS.forEach(tool => {
      if (!groups.has(tool.categoryName)) {
        groups.set(tool.categoryName, []);
      }
      groups.get(tool.categoryName)?.push(tool);
    });

    const categoryOrder = [
      'PDF Conversion',
      'Office Conversion',
      'Image Conversion',
      'Video Conversion',
      'Audio Conversion',
      'JSON Conversion',
      'XML Conversion',
      'CSV Conversion',
      'OCR Conversion',
      'Website Conversion',
      'Subtitle Conversion',
      'Markdown Conversion',
      'Text Conversion',
      'E-Book Conversion',
      'File Formatter'
    ];

    this.categoriesWithTools = Array.from(groups.entries())
      .map(([name, tools]) => {
        const categoryInfo = TOOLS_CATEGORIES.find(c => c.title.includes(name));
        return {
          name,
          icon: categoryInfo?.icon || 'fas fa-tools',
          count: tools.length,
          tools
        };
      })
      .sort((a, b) => {
        const indexA = categoryOrder.indexOf(a.name);
        const indexB = categoryOrder.indexOf(b.name);
        return (indexA > -1 ? indexA : 99) - (indexB > -1 ? indexB : 99);
      });
  }

  getCategoryClass(categoryName: string): string {
    const name = categoryName.toLowerCase();
    if (name.includes('pdf')) return 'cat-pdf';
    if (name.includes('office')) return 'cat-office';
    if (name.includes('image')) return 'cat-image';
    if (name.includes('video')) return 'cat-video';
    if (name.includes('audio')) return 'cat-audio';
    if (name.includes('json')) return 'cat-json';
    if (name.includes('xml')) return 'cat-xml';
    if (name.includes('csv')) return 'cat-csv';
    if (name.includes('ocr')) return 'cat-ocr';
    if (name.includes('website')) return 'cat-website';
    if (name.includes('subtitle')) return 'cat-subtitle';
    if (name.includes('markdown')) return 'cat-markdown';
    if (name.includes('text')) return 'cat-text';
    if (name.includes('e-book')) return 'cat-ebook';
    if (name.includes('formatter')) return 'cat-formatter';
    return '';
  }

  getSourceFormatClass(toolId: string): string {
    const id = toolId.toLowerCase();
    if (id.includes('-to-')) {
      const parts = id.split('-to-');
      return 'fmt-' + parts[0].trim();
    }
    // Special cases
    if (id.includes('xml')) return 'fmt-xml';
    if (id.includes('srt')) return 'fmt-srt';
    if (id.includes('vtt')) return 'fmt-vtt';
    if (id.includes('json')) return 'fmt-json';
    if (id.includes('csv')) return 'fmt-csv';
    if (id.includes('pdf')) return 'fmt-pdf';
    return '';
  }

  getTargetFormatClass(toolId: string): string {
    const id = toolId.toLowerCase();
    if (id.includes('-to-')) {
      const parts = id.split('-to-');
      const targetPart = parts[1].split('-')[0].trim();
      return 'fmt-' + targetPart;
    }
    // Special cases (usually same as source for validators/translators)
    if (id.includes('xml')) return 'fmt-xml';
    if (id.includes('srt')) return 'fmt-srt';
    if (id.includes('vtt')) return 'fmt-vtt';
    if (id.includes('json')) return 'fmt-json';
    if (id.includes('csv')) return 'fmt-csv';
    if (id.includes('pdf')) return 'fmt-pdf';
    return '';
  }

  groupedSearchResults: { name: string, icon: string, tools: SearchableTool[] }[] = [];

  onSearchChange() {
    if (!this.searchQuery.trim()) {
      this.isSearching = false;
      this.searchResults = [];
      this.groupedSearchResults = [];
      return;
    }

    const query = this.searchQuery.toLowerCase();
    const filtered = ALL_TOOLS.filter(tool => 
      tool.title.toLowerCase().includes(query) || 
      tool.categoryName.toLowerCase().includes(query)
    );

    // Group the filtered tools by category
    const groups = new Map<string, SearchableTool[]>();
    filtered.forEach(tool => {
      if (!groups.has(tool.categoryName)) {
        groups.set(tool.categoryName, []);
      }
      groups.get(tool.categoryName)?.push(tool);
    });

    this.groupedSearchResults = Array.from(groups.entries()).map(([name, tools]) => {
      const categoryInfo = TOOLS_CATEGORIES.find(c => c.title.includes(name));
      return {
        name,
        icon: categoryInfo?.icon || 'fas fa-tools',
        tools
      };
    });

    this.searchResults = filtered; // Keep for total count
    this.isSearching = true;
  }

  clearSearch() {
    this.searchQuery = '';
    this.isSearching = false;
    this.searchResults = [];
  }
}
