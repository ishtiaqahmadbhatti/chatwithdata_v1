import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseMarkdownToolComponent } from '../base-markdown-tool.component';

@Component({
    selector: 'app-markdown-to-word',
    imports: [CommonModule, FormsModule, FileConversionUiComponent],
    templateUrl: './markdown-to-word.component.html',
    styleUrl: './markdown-to-word.component.css',
    standalone: true
})
export class MarkdownToWordComponent extends BaseMarkdownToolComponent {
    toolId = 'markdown-to-word';
}
