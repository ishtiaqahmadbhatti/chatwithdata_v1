import { Component, OnInit, HostListener, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseSubtitleToolComponent } from '../base-subtitle-tool.component';

@Component({
  selector: 'app-translate-srt',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './translate-srt.component.html',
  styleUrl: './translate-srt.component.css',
  standalone: true
})
export class TranslateSrtComponent extends BaseSubtitleToolComponent implements OnInit {
  toolId = 'translate-srt';

  supportedLanguages: any = {};
  languageKeys: string[] = [];
  sourceLanguage: string = 'auto';
  targetLanguage: string = 'en';

  isSourceDropdownOpen: boolean = false;
  isTargetDropdownOpen: boolean = false;

  @ViewChild('sourceContainer') sourceContainer!: ElementRef;
  @ViewChild('targetContainer') targetContainer!: ElementRef;

  constructor(private eRef: ElementRef) {
    super();
  }

  ngOnInit(): void {
    this.subtitleService.getSupportedLanguages().subscribe({
      next: (response) => {
        if (response && response.success && response.languages) {
          this.supportedLanguages = response.languages;
          this.languageKeys = Object.keys(this.supportedLanguages);
        }
      },
      error: (error) => {
        console.error('Failed to load supported languages', error);
      }
    });
  }

  toggleSourceDropdown(event: Event): void {
    event.stopPropagation();
    this.isSourceDropdownOpen = !this.isSourceDropdownOpen;
    this.isTargetDropdownOpen = false;
  }

  toggleTargetDropdown(event: Event): void {
    event.stopPropagation();
    this.isTargetDropdownOpen = !this.isTargetDropdownOpen;
    this.isSourceDropdownOpen = false;
  }

  selectSourceLanguage(key: string): void {
    this.sourceLanguage = key;
    this.isSourceDropdownOpen = false;
  }

  selectTargetLanguage(key: string): void {
    this.targetLanguage = key;
    this.isTargetDropdownOpen = false;
  }

  getSourceLanguageName(): string {
    if (this.sourceLanguage === 'auto') return 'Auto Detect';
    const key = this.languageKeys.find(k => this.supportedLanguages[k] === this.sourceLanguage);
    return key ? key.charAt(0).toUpperCase() + key.slice(1) : this.sourceLanguage;
  }

  getTargetLanguageName(): string {
    const key = this.languageKeys.find(k => this.supportedLanguages[k] === this.targetLanguage);
    return key ? key.charAt(0).toUpperCase() + key.slice(1) : this.targetLanguage;
  }

  @HostListener('document:click', ['$event'])
  clickout(event: Event) {
    if (this.sourceContainer && !this.sourceContainer.nativeElement.contains(event.target)) {
      this.isSourceDropdownOpen = false;
    }
    if (this.targetContainer && !this.targetContainer.nativeElement.contains(event.target)) {
      this.isTargetDropdownOpen = false;
    }
  }

  override getConversionOptions(): Record<string, string> {
    return {
      source_language: this.sourceLanguage,
      target_language: this.targetLanguage
    };
  }
}
