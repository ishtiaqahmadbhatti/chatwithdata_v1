import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-to-excel.component.html',
  styleUrl: './json-to-excel.component.css',
  standalone: true
})
export class JsonToExcelComponent extends BaseJsonToolComponent {
  toolId = 'json-to-excel';
}
