import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseFileFormatterToolComponent } from '../base-file-formatter-tool.component';

@Component({
  selector: 'app-minify-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './minify-json.component.html',
  styleUrl: './minify-json.component.css',
  standalone: true
})
export class MinifyJsonComponent extends BaseFileFormatterToolComponent {
  toolId = 'minify-json';
}
