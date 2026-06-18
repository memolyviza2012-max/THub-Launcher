# Thub - Cloud Launcher and Modding Tools
# Copyright (C) 2026 Danaiwit Kanthawong (NodNuatTranslator)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

path = 'E:/Mod_Workspace/Modder_project/modder-hub/tools/TStudio/tstudio_app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

if 'ðŸ” Search' in text or '\ufffd Search' in text:
    print('MOJIBAKE FOUND')
else:
    print('NO MOJIBAKE')
