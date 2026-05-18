import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseMarkdownToolComponent } from '../base-markdown-tool.component';

@Component({
    selector: 'app-word-to-markdown',
    imports: [CommonModule, FormsModule, FileConversionUiComponent],
    templateUrl: './word-to-markdown.component.html',
    styleUrl: './word-to-markdown.component.css',
    standalone: true
})
export class WordToMarkdownComponent extends BaseMarkdownToolComponent {
    toolId = 'word-to-markdown';
}
