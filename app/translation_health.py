"""Local project budgets, never a claim about the account's Cloud credit."""


def summarize(rows, budget):
    budget = max(1, min(500_000, int(budget)))
    groups = {}
    for row in rows:
        group = groups.setdefault(row['project'], {'project': row['project'], 'keys': [], 'used': 0})
        group['keys'].append(row)
        group['used'] = max(group['used'], max(0, row.get('used', 0)))
    output = []
    for group in groups.values():
        keys = group.pop('keys')
        used = group['used']
        percent = min(100, round(used * 100 / budget))
        level = 'exhausted' if used >= budget else 'critical' if used * 100 >= budget * 95 else 'warning' if used * 100 >= budget * 80 else 'normal'
        blocked = all(row.get('blocked') for row in keys)
        output.append({**group, 'keyCount': len(keys), 'remaining': max(0, budget-used),
                       'budget': budget, 'percent': percent, 'level': level, 'blocked': blocked,
                       'unverified': group['project'] == 'mặc định' and len(keys) > 1})
    usable = [row for row in output if row['remaining'] and not row['blocked']]
    warning = not rows or not usable or any(row['level'] != 'normal' or row['blocked'] for row in output)
    return {'groups': output, 'used': sum(row['used'] for row in output),
            'remaining': sum(row['remaining'] for row in usable), 'budget': budget,
            'configured': bool(rows), 'available': bool(usable), 'warning': warning,
            'unverified': any(row['unverified'] for row in output),
            'status': 'Chưa có key' if not rows else 'Cần kiểm tra giới hạn/key' if not usable else
                      'Gần giới hạn đã đặt' if warning else 'Trong giới hạn đã đặt'}
