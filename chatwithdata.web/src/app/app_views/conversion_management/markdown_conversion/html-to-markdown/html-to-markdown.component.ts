import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseMarkdownToolComponent } from '../base-markdown-tool.component';

@Component({
    selector: 'app-html-to-markdown',
    imports: [CommonModule, FormsModule, FileConversionUiComponent],
    templateUrl: './html-to-markdown.component.html',
    styleUrl: './html-to-markdown.component.css',
    standalone: true
})
export class HtmlToMarkdownComponent extends BaseMarkdownToolComponent {
    toolId = 'html-to-markdown';
}
