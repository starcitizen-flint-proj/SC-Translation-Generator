1. `μSCU` / `µ标准货物单位`: 改为`uSCU`
2. `RR_([A-Z]{3})_(L\d)`: （目前是斯坦顿的）拉格朗日点，简化双语名称
3. `item_NameFood.*` / `item_NameDrind.*`: 食物/饮料：双语+数据
   - 注：NDR为饱食度，HEI为口渴度
4. `items_commodities`(后面没有desc的): 商品，双语换行
5. vehicle_Name / vehicle_name: 载具名称，双语不换行 / 纯英文 / 特殊处理
   - 有个特殊的_short后缀代表短名称（无厂商），可以用那个做混搭