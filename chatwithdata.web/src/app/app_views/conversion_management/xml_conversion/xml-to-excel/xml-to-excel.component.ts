import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-xml-to-excel',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xml-to-excel.component.html',
  styleUrl: './xml-to-excel.component.css',
  standalone: true
})
export class XmlToExcelComponent extends BaseXmlToolComponent {
  toolId = 'xml-to-excel';
}
