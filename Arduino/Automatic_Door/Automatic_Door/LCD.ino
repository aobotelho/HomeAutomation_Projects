void ClearLine(int line,int columns,int rows,LiquidCrystal_I2C lcd_var){
  lcd_var.setCursor(0,line);
  for(int i=0;i<columns;i++){
    lcd_var.print(" ");
  }
  lcd_var.setCursor(0,line);
}
