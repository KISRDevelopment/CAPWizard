def generate_cap_table(title, units, adb_df, only_output, exclude_secondary_op_modes, eqn_func, precision=4):
     cap = f'title: {title}\nunit: {units}, 1.\ndirection: hor\npostdigits: {precision}\n@\n'
     adb_df = adb_df.copy()
     if only_output:
          adb_df = adb_df[adb_df['type'] == 'main output']
     if exclude_secondary_op_modes:
          adb_df['tech_code'] = adb_df['tech_code'].str.replace(r'\[\d+\.\]', '', regex=True)
          adb_df = adb_df[['tech_code', 'type', 'level_code','form_code', 'full_code']].drop_duplicates(subset=['tech_code', 'type'], keep='first')
     adb_df['eqn'] = adb_df.apply(eqn_func, axis=1)
     cap += '\n'.join(adb_df['eqn'].tolist())
     return cap
