import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseEbookToolComponent } from '../base-ebook-tool.component';

@Component({
  selector: 'app-markdown-to-epub',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './markdown-to-epub.component.html',
  styleUrl: './markdown-to-epub.component.css',
  standalone: true
})
export class MarkdownToEpubComponent extends BaseEbookToolComponent {
  toolId = 'markdown-to-epub';

  // Additional fields for Markdown to EPUB conversion
  bookTitle: string = 'Converted Book';
  authorName: string = 'Unknown';

  // Override to provide extra parameters for the conversion
  protected override getExtraParams(): { [key: string]: string } {
    return {
      'title': this.bookTitle.trim() || 'Converted Book',
      'author': this.authorName.trim() || 'Unknown'
    };
  }

  // Override reset to also clear the extra fields
  override reset(): void {
    super.reset();
    this.bookTitle = 'Converted Book';
    this.authorName = 'Unknown';
  }
}
