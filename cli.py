"""
命令行界面
提供交互式的命令行工具，用于运行工作流和管理技能
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from agents.agentscope.integrator import AgentIntegrator
from config_agentscope import validate_config
from main import run_daily_workflow

console = Console()


@click.group()
def cli():
    """
    教师智能体工作流命令行工具
    """
    pass


@cli.command()
@click.option('--student-id', default='student_001', help='学生ID')
@click.option('--skill-title', default='同步与互斥教学案例', help='技能标题')
def workflow(student_id, skill_title):
    """
    运行完整工作流
    """
    console.print(Panel(f"运行工作流: 学生={student_id}, 技能={skill_title}", title="工作流启动"))
    
    try:
        result = run_daily_workflow(student_id, skill_title)
        
        # 提取评分结果
        grad_res = result.get("grading_result", {})
        score = grad_res.get("total_score", "N/A")
        feedback = grad_res.get("overall_feedback", "无评价")
        
        # 提取分析报告
        report = result.get("analysis_report", {})
        trend = report.get("trend", "数据不足")
        suggestion = report.get("suggestion", "继续保持")

        console.print(Panel(
            f"📝 本次测试得分: {score} 分\n"\
            f"📈 进步趋势评估: {trend}\n"\
            f"💡 学习专家建议: {suggestion}\n"\
            f"🔄 是否触发复测: {'是 (请查阅新题目)' if result.get('need_retry') else '否 (已达标)'}",
            title="工作流执行完成"
        ))
        
    except Exception as e:
        console.print(Panel(f"❌ 工作流运行失败: {e}", title="错误"))


@cli.command()
@click.option('--chat-model', default='gpt-3.5-turbo', help='聊天模型')
@click.option('--router-model', default='gpt-3.5-turbo', help='路由模型')
@click.option('--skills-dir', default='skills', help='技能目录')
@click.option('--max-skills', default=3, help='最大技能数量')
@click.option('--show-routing', is_flag=True, help='显示路由决策')
def chat(chat_model, router_model, skills_dir, max_skills, show_routing):
    """
    启动交互式聊天界面
    """
    # 验证配置
    is_valid, error_msg = validate_config()
    if not is_valid:
        console.print(Panel(f"❌ 配置错误: {error_msg}", title="错误"))
        return
    
    console.print(Panel(
        f"聊天模型: {chat_model}\n"\
        f"路由模型: {router_model}\n"\
        f"技能目录: {skills_dir}\n"\
        f"最大技能数: {max_skills}",
        title="聊天界面启动"
    ))
    
    try:
        # 初始化集成器
        integrator = AgentIntegrator(
            chat_model_name=chat_model,
            router_model_name=router_model,
            skills_dir=skills_dir,
            max_skills=max_skills,
        )
        
        # 显示可用技能
        skills = integrator.get_available_skills()
        if skills:
            console.print(Panel(f"发现 {len(skills)} 个技能", title="可用技能"))
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("技能名称")
            table.add_column("描述")
            for skill in skills:
                table.add_row(skill['name'], skill.get('description', '无描述'))
            console.print(table)
        else:
            console.print(Panel("未发现技能", title="警告"))
        
        # 交互式聊天
        console.print(Panel("输入 'exit' 退出聊天", title="提示"))
        
        while True:
            user_input = console.input("[bold green]你: [/]")
            
            if user_input.lower() == 'exit':
                console.print(Panel("聊天结束", title="再见"))
                break
            
            # 处理查询
            result = integrator.process_query(user_input)
            
            # 显示路由决策
            if show_routing:
                if result['use_skills']:
                    skills_text = ", ".join(result['selected_skills'])
                    console.print(Panel(
                        f"使用技能: {skills_text}\n"\
                        f"理由: {result['rationale']}",
                        title="路由决策"
                    ))
                else:
                    console.print(Panel(
                        f"未使用技能\n"\
                        f"理由: {result['rationale']}",
                        title="路由决策"
                    ))
            
            # 显示响应
            console.print(Panel(result['response'], title="助手"))
            
    except Exception as e:
        console.print(Panel(f"❌ 聊天界面启动失败: {e}", title="错误"))


@cli.command()
def list_skills():
    """
    列出所有可用技能
    """
    from utils.skill_loader import discover_skills
    
    skills = discover_skills()
    
    if skills:
        console.print(Panel(f"发现 {len(skills)} 个技能", title="可用技能"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("技能名称")
        table.add_column("描述")
        table.add_column("格式")
        
        for skill in skills:
            # 检测技能格式
            if 'when_to_use' in skill and skill['when_to_use']:
                format_type = "标准 SKILL.md"
            else:
                format_type = "传统格式"
            
            table.add_row(
                skill['name'],
                skill.get('description', '无描述'),
                format_type
            )
        
        console.print(table)
    else:
        console.print(Panel("未发现技能", title="提示"))


@cli.command()
def validate():
    """
    验证配置
    """
    is_valid, error_msg = validate_config()
    
    if is_valid:
        console.print(Panel("配置验证通过", title="成功"))
    else:
        console.print(Panel(f"配置验证失败: {error_msg}", title="错误"))


if __name__ == '__main__':
    cli()