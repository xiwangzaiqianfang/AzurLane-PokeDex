import requests
import dataclasses
import json
import os
from models import Ship
from typing import Optional

class ShipManager:
    REQUIRED_FIELDS = set(Ship.__dataclass_fields__.keys())

    def __init__(self, filepath="ships.json"):
        self.filepath = filepath
        self.version = "0.0"
        self.ships: list[Ship] = []
        self.load()

    def load(self):
        """加载 JSON，若不存在则创建示例数据"""
        if not os.path.exists(self.filepath):
            self._create_sample_data()
            return

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            print(f"[DEBUG] 原始数据类型: {type(raw_data)}")
            if isinstance(raw_data, dict):
                print(f"[DEBUG] 字典键: {list(raw_data.keys())}")

                # 兼容旧版本：如果 data 是列表，则包装成新格式
                if isinstance(raw_data, dict) and "version" in raw_data and "ships" in raw_data:
                    self.version = raw_data.get("version", "0.0")
                    ships_data = raw_data["ships"]
                    print(f"[DEBUG] 新版格式，version={self.version}, ships_data 类型={type(ships_data)}")
                elif isinstance(raw_data, list):
                    # 旧版格式：直接是数组
                    self.version = "0.0"
                    ships_data = raw_data
                    print(f"[DEBUG] 旧版格式，直接数组，长度={len(ships_data)}")
                else:
                    # 未知格式，尝试补救
                    print("[ERROR] 无法识别的数据格式，将重置为空")
                    self.version = "0.0"
                    ships_data = []

                # 确保 ships_data 是列表
            if not isinstance(ships_data, list):
                ships_data = []  # 如果意外不是列表，重置为空

            ship_fields = set(Ship.__dataclass_fields__.keys())
            migrated = []

            for item in ships_data:
                # 旧数据迁移：如果存在旧式单字段科技点，将其转换为三阶段字段
                #self._migrate_old_tech_fields(item)
                if not isinstance(item, dict):
                    print(f"警告: 遇到非字典数据，已跳过: {item}")
                    continue
                
                # 补全所有缺失字段
                for field in ship_fields:
                    if field not in item:
                        default_val = Ship.__dataclass_fields__[field].default
                        if default_val is dataclasses._MISSING_TYPE:
                            # 必需字段缺失，根据类型设置合理的默认值
                            field_type = Ship.__dataclass_fields__[field].type
                            if field_type == int:
                                item[field] = 0          # 例如 id 默认 0
                            elif field_type == str:
                                item[field] = ""          # 名称等默认空字符串
                            elif field_type == bool:
                                item[field] = False
                            elif field_type == list:
                                item[field] = []           # drop_locations 等列表
                            else:
                                item[field] = None
                        else:
                            item[field] = default_val  

                # 处理 drop_locations 字符串转列表
                if isinstance(item.get('drop_locations'), str):
                    item['drop_locations'] = item['drop_locations'].split(';') if item['drop_locations'] else []

                # 仅保留合法字段
                filtered_item = {k: v for k, v in item.items() if k in ship_fields}
                migrated.append(filtered_item)

            # 转换为 Ship 对象
            self.ships = [Ship.from_dict(item) for item in migrated]
            print(f"[INFO] 成功加载 {len(self.ships)} 条舰船，版本 {self.version}")
            #self.version = version   # 可以在类中保存版本号

            # 如果检测到旧格式，立即保存为新格式（可选）
            #if isinstance(data, list):
            #    self.save()   # 这会以新格式保存

        except json.JSONDecodeError as e:
            raise Exception(f"JSON 文件损坏: {e}\n请使用在线校验工具修复或恢复备份。")

    def _migrate_old_tech_fields(self, item: dict):
        """
        将旧版本的单字段科技点（如 tech_durability）转换为三阶段字段
        （获得阶段赋原值，满破和120阶段置0）
        """
        tech_bases = [
            "tech_durability", "tech_firepower", "tech_torpedo", "tech_aa",
            "tech_aviation", "tech_accuracy", "tech_reload", "tech_mobility", "tech_antisub"
        ]
        for base in tech_bases:
            old_key = base
            if old_key in item and isinstance(item[old_key], (int, float)):
                # 将原值赋给获得阶段
                item[f"{base}_obtain"] = int(item[old_key])
                # 如果满破/120阶段不存在，则设为0
                if f"{base}_max" not in item:
                    item[f"{base}_max"] = 0
                if f"{base}_120" not in item:
                    item[f"{base}_120"] = 0
                # 删除旧字段
                del item[old_key]

    def save(self):
        """保存到 JSON，包含版本号，使用原子写入防止文件损坏"""
        # 检查 self.ships 是否全部是 Ship 对象
        for i, s in enumerate(self.ships):
            if not isinstance(s, Ship):
                print(f"错误: ships[{i}] 不是 Ship 对象: {s}")
                # 这里可以选择抛出异常或尝试修复
                raise TypeError(f"ships[{i}] 不是 Ship 对象")
    
        data_to_save = {
            "version": self.version,
            "ships": [s.to_dict() for s in self.ships]
        }
    
        # 先写入临时文件，再替换原文件
        temp_file = self.filepath + ".tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.filepath)
            print(f"[保存成功] {self.filepath} 版本 {self.version}，舰船数 {len(self.ships)}")
        except Exception as e:
            print(f"[保存失败] {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise


    def _create_sample_data(self):
        sample = [
            Ship(
                id=1, name="泛用型布里", faction="其他", ship_class="驱逐", rarity="精锐",
                owned=False, breakthrough=0, oath=False, level_120=False, acquire_main="兑换、赠送", acquire_detail="日/周常任务、月度签到、活动任务、商店兑换、主线普通关卡三星奖励、新兵训练、礼包购买", shop_exchange="勋章、演习", release_date="2017年05月25日", notes="无法建造",
                tech_durability_obtain=0, tech_durability_max=0, tech_durability_120=0,
                tech_firepower_obtain=0, tech_firepower_max=0, tech_firepower_120=0,
                tech_torpedo_obtain=0, tech_torpedo_max=0, tech_torpedo_120=0,
                tech_aa_obtain=0, tech_aa_max=0, tech_aa_120=0,
                tech_aviation_obtain=0, tech_aviation_max=0, tech_aviation_120=0,
                tech_accuracy_obtain=0, tech_accuracy_max=0, tech_accuracy_120=0,
                tech_reload_obtain=0, tech_reload_max=0, tech_reload_120=0,
                tech_mobility_obtain=0, tech_mobility_max=0, tech_mobility_120=0,
                tech_antisub_obtain=0, tech_antisub_max=0, tech_antisub_120=0,
                image_path="images/bulin.png"
            ),
            Ship(
                id=2, name="试作型布里MKII", faction="其他", ship_class="驱逐", rarity="超稀有",
                owned=False, breakthrough=0, oath=False, level_120=False, acquire_main="兑换、赠送", acquire_detail="日/周常任务、月度签到、活动任务、商店兑换、主线普通关卡三星奖励、新兵训练、礼包购买", shop_exchange="勋章、演习", release_date="2017年05月25日", notes="无法建造",
                tech_durability_obtain=0, tech_durability_max=0, tech_durability_120=0,
                tech_firepower_obtain=0, tech_firepower_max=0, tech_firepower_120=0,
                tech_torpedo_obtain=0, tech_torpedo_max=0, tech_torpedo_120=0,
                tech_aa_obtain=0, tech_aa_max=0, tech_aa_120=0,
                tech_aviation_obtain=0, tech_aviation_max=0, tech_aviation_120=0,
                tech_accuracy_obtain=0, tech_accuracy_max=0, tech_accuracy_120=0,
                tech_reload_obtain=0, tech_reload_max=0, tech_reload_120=0,
                tech_mobility_obtain=0, tech_mobility_max=0, tech_mobility_120=0,
                tech_antisub_obtain=0, tech_antisub_max=0, tech_antisub_120=0,
                image_path="images/trial_bulin_mkii.png"
            )
        ]
        self.ships = sample
        self.version = "0.1"
        self.save()

    def filter(self, criteria: dict) -> list[Ship]:
        result = self.ships[:]
        for field, value in criteria.items():
            if value is None or value == "":
                continue
            if field == "faction":
                result = [s for s in result if s.faction == value]
            elif field == "ship_class":
                result = [s for s in result if s.ship_class == value]
            elif field == "rarity":
                result = [s for s in result if s.rarity == value]
            elif field == "can_remodel" and value:
                result = [s for s in result if s.can_remodel]
            elif field == "remodeled" and value:
                result = [s for s in result if s.remodeled]
            elif field == "oath" and value:
                result = [s for s in result if s.oath]
            elif field == "owned" and value:
                result = [s for s in result if s.owned]
            elif field == "max_breakthrough" and value:
                result = [s for s in result if s.is_max_breakthrough()]
            elif field == "level_120" and value:
                result = [s for s in result if s.level_120]
        return result

    def sort(self, ships: list[Ship], key: str, reverse: bool = False) -> list[Ship]:
        if key == "id":
            return sorted(ships, key=lambda s: s.id, reverse=reverse)
        elif key == "name":
            return sorted(ships, key=lambda s: s.name, reverse=reverse)
        elif key == "rarity":
            rarity_order = {"普通":1, "稀有":2, "精锐":3, "超稀有":4, "海上传奇":5}
            return sorted(ships, key=lambda s: rarity_order.get(s.rarity, 0), reverse=reverse)
        return ships

    def stats(self):
        not_owned = [s for s in self.ships if not s.owned]
        owned_not_max = [s for s in self.ships if s.owned and not s.is_max_breakthrough()]
        return len(not_owned), len(owned_not_max)

    def add_ship(self, ship: Ship):
        """添加新船，若 ship.id 为 0 则自动分配，否则检查冲突并可能自动调整"""
        existing_ids = {s.id for s in self.ships}
        
        if ship.id == 0:
            # 自动分配：取最大 ID + 1
            max_id = max(existing_ids, default=0)
            new_id = max_id + 1
            # 确保新 ID 不冲突（如果 max_id+1 意外被占用？但理论上不会，因为 existing_ids 已包含所有）
            while new_id in existing_ids:
                new_id += 1  # 极罕见情况，但保留
            ship.id = new_id
        else:
            # 手动指定 ID，检查是否冲突
            if ship.id in existing_ids:
                # 冲突处理：弹窗询问用户是否自动分配新 ID，或抛出异常
                # 这里我们选择自动分配新 ID 并给出警告
                print(f"警告：ID {ship.id} 已存在，将自动分配新 ID")
                max_id = max(existing_ids, default=0)
                new_id = max_id + 1
                while new_id in existing_ids:
                    new_id += 1
                ship.id = new_id
                # 可选：通过信号或返回值通知用户
            # 如果未冲突，直接使用 ship.id

        self.ships.append(ship)
        self.save()
        print(f"已添加舰船 ID={ship.id}, 当前总数为 {len(self.ships)}")
        return ship.id

    def switch_file(self, new_path):
        self.filepath = new_path
        self.load()

    def export_csv(self, path):
        import pandas as pd
        df = pd.DataFrame([s.to_dict() for s in self.ships])
        df.to_csv(path, index=False, encoding='utf-8-sig')

    def export_excel(self, path):
        import pandas as pd
        df = pd.DataFrame([s.to_dict() for s in self.ships])
        df.to_excel(path, index=False)

    def import_csv(self, path):
        import pandas as pd
        df = pd.read_csv(path, encoding='utf-8-sig')
        ships = []
        for _, row in df.iterrows():
            data = row.to_dict()
            for field in self.REQUIRED_FIELDS:
                if field not in data:
                    data[field] = Ship.__dataclass_fields__[field].default
            ships.append(Ship.from_dict(data))
        self.ships = ships
        self.save()

    def update_from_github(self, url: str, backup: bool = True) -> bool:
        """
        从远程 URL 更新舰船数据
        :param url: 远程 JSON 文件的 URL
        :param backup: 是否在更新前备份当前文件
        :return: 是否成功
        """
        import requests
        import os
        import shutil
        try:
            print(f"正在从 {url} 获取最新数据...")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            remote_data = resp.json()

            # 验证数据格式（至少包含一条记录，且每条记录有 id 和 name）
            if isinstance(remote_data, dict) and "version" in remote_data and "ships" in remote_data:
                remote_version = remote_data.get("version", "0.0")
                remote_ships = remote_data.get("ships", [])
            elif isinstance(remote_data, list):
                remote_version = "0.0"   # 假设旧格式版本为1.0
                remote_ships = remote_data
            else:
                raise ValueError("远程数据格式错误")
            
            # 比较版本
            if self._version_compare(remote_version, self.version) <= 0:
                print("远程版本不高于本地版本，无需更新")
                return False

            # 备份当前文件
            if backup and os.path.exists(self.filepath):
                backup_path = self.filepath + ".bak"
                shutil.copy2(self.filepath, backup_path)
                print(f"已备份当前数据到 {backup_path}")

            # 数据迁移：确保新数据包含所有必要字段
            ship_fields = set(Ship.__dataclass_fields__.keys())
            migrated = []
            for item in remote_ships:
                # 补全缺失字段
                for field in ship_fields:
                    if field not in item:
                        default_val = Ship.__dataclass_fields__[field].default
                        item[field] = default_val
                # 处理 drop_locations 字符串转列表
                if isinstance(item.get('drop_locations'), str):
                    item['drop_locations'] = item['drop_locations'].split(';') if item['drop_locations'] else []
                # 仅保留合法字段
                filtered_item = {k: v for k, v in item.items() if k in ship_fields}
                migrated.append(filtered_item)

            # 将新数据转换为 Ship 对象列表
            new_ships = [Ship.from_dict(item) for item in migrated]

            # **重要：合并用户数据**（保留用户的拥有状态、突破数等）
            self._merge_user_data(new_ships)

            # 替换当前数据
            self.ships = new_ships
            self.version = remote_version
            self.save()
            print("数据更新成功！")
            return True

        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            raise Exception(f"网络更新失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            raise Exception(f"远程数据格式错误: {e}")
        except Exception as e:
            print(f"更新过程中发生错误: {e}")
            raise

    def _version_compare(self, v1, v2):
        """比较两个版本号，v1 > v2 返回正数，相等返回0，v1 < v2 返回负数"""
        def normalize(v):
            return [int(x) for x in v.split('.')]
        v1_parts = normalize(v1)
        v2_parts = normalize(v2)
        # 补零使长度相同
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        else:
            return 0

    def _merge_user_data(self, new_ships: list):
        """
        将当前用户数据（拥有状态、突破数等）合并到新数据中
        策略：以新数据为基础，如果旧数据中有相同 ID 的船，则保留用户的 owned、breakthrough、oath、level_120 等状态
        """
        # 建立旧数据字典，以 ID 为键
        old_dict = {s.id: s for s in self.ships}

        for new_ship in new_ships:
            old_ship = old_dict.get(new_ship.id)
            if old_ship:
                # 保留用户的自定义状态
                new_ship.owned = old_ship.owned
                new_ship.breakthrough = old_ship.breakthrough
                new_ship.oath = old_ship.oath
                new_ship.level_120 = old_ship.level_120
                # 如果还保留了其他状态（如改造、誓约等），也可一并合并
                new_ship.remodeled = old_ship.remodeled
                # 注意：科技点数值以新数据为准（因为可能修正了数值）